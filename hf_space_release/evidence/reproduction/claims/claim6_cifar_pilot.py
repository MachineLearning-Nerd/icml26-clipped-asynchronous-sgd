"""Real CIFAR-10 pilot for the heterogeneous Figure 4 claim."""

from __future__ import annotations

import concurrent.futures
import heapq
import json
import math
import os
import random
import statistics
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torchvision import datasets


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / ".openresearch" / "artifacts" / "claim6_cifar_pilot"
CIFAR_HF_MIRROR = (
    "https://huggingface.co/datasets/VerisimilitudeX/cifar10/resolve/main/"
    "cifar-10-python.tar.gz"
)
SEED = 20260729
CLIENTS = 16
DIRICHLET_ALPHA = 0.5
BATCH_SIZE = 64
DELAY_FACTOR = 4
TIME_CAP = 3_200.0
EVAL_INTERVAL = 100.0
TARGET_ACCURACY = 0.70
PROCESS_WORKERS = 3
THREADS_PER_PROCESS = 2
_THREADS_CONFIGURED = False

TRAIN_IMAGES: np.ndarray | None = None
TRAIN_LABELS: np.ndarray | None = None
TEST_IMAGES: np.ndarray | None = None
TEST_LABELS: np.ndarray | None = None


@dataclass(frozen=True)
class PilotConfig:
    name: str
    learning_rate: float
    clipping_radius: float | None


CONFIGS = (
    PilotConfig("vanilla_lr_2^-6", 2.0**-6, None),
    PilotConfig("clipped_lr_2^-4_c1", 2.0**-4, 1.0),
    PilotConfig("clipped_lr_2^-4_c2", 2.0**-4, 2.0),
)


class TwoConvCNN(nn.Module):
    """Common federated CIFAR CNN: two convolutions and two dense layers."""

    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=5),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=5),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Linear(64 * 5 * 5, 512),
            nn.ReLU(),
            nn.Linear(512, 10),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        features = self.features(inputs)
        return self.classifier(torch.flatten(features, 1))


def set_determinism(seed: int) -> None:
    global _THREADS_CONFIGURED
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if not _THREADS_CONFIGURED:
        torch.set_num_threads(THREADS_PER_PROCESS)
        torch.set_num_interop_threads(1)
        _THREADS_CONFIGURED = True
    torch.use_deterministic_algorithms(True)


def dirichlet_partition(labels: np.ndarray, seed: int) -> list[np.ndarray]:
    """Assign every training example once using class-wise Dirichlet draws."""
    rng = np.random.default_rng(seed)
    clients: list[list[int]] = [[] for _ in range(CLIENTS)]
    for label in range(10):
        indices = np.flatnonzero(labels == label)
        rng.shuffle(indices)
        proportions = rng.dirichlet(np.full(CLIENTS, DIRICHLET_ALPHA))
        boundaries = np.cumsum(proportions)[:-1]
        splits = np.split(indices, np.floor(boundaries * len(indices)).astype(int))
        for client, split in zip(clients, splits, strict=True):
            client.extend(int(index) for index in split)
    arrays = []
    for client in clients:
        values = np.asarray(client, dtype=np.int64)
        rng.shuffle(values)
        arrays.append(values)
    return arrays


class ClientSampler:
    def __init__(self, indices: np.ndarray, seed: int) -> None:
        if len(indices) < BATCH_SIZE:
            raise ValueError("client partition smaller than batch size")
        self.indices = indices.copy()
        self.rng = np.random.default_rng(seed)
        self.position = len(indices)

    def next_batch(self) -> np.ndarray:
        if self.position + BATCH_SIZE > len(self.indices):
            self.rng.shuffle(self.indices)
            self.position = 0
        batch = self.indices[self.position : self.position + BATCH_SIZE]
        self.position += BATCH_SIZE
        return batch


def normalized_batch(images: np.ndarray, indices: np.ndarray) -> torch.Tensor:
    batch = torch.from_numpy(images[indices]).permute(0, 3, 1, 2).float().div_(255.0)
    mean = torch.tensor((0.4914, 0.4822, 0.4465)).view(1, 3, 1, 1)
    std = torch.tensor((0.2470, 0.2435, 0.2616)).view(1, 3, 1, 1)
    return batch.sub_(mean).div_(std)


def test_accuracy(model: nn.Module) -> float:
    assert TEST_IMAGES is not None and TEST_LABELS is not None
    model.eval()
    correct = 0
    with torch.inference_mode():
        for start in range(0, len(TEST_LABELS), 512):
            indices = np.arange(start, min(start + 512, len(TEST_LABELS)))
            inputs = normalized_batch(TEST_IMAGES, indices)
            targets = torch.from_numpy(TEST_LABELS[indices])
            correct += int((model(inputs).argmax(dim=1) == targets).sum())
    model.train()
    return correct / len(TEST_LABELS)


def compute_gradient(
    model: nn.Module, sampler: ClientSampler
) -> tuple[list[torch.Tensor], float]:
    assert TRAIN_IMAGES is not None and TRAIN_LABELS is not None
    indices = sampler.next_batch()
    inputs = normalized_batch(TRAIN_IMAGES, indices)
    targets = torch.from_numpy(TRAIN_LABELS[indices])
    model.zero_grad(set_to_none=True)
    loss = nn.functional.cross_entropy(model(inputs), targets)
    loss.backward()
    gradients = [
        parameter.grad.detach().clone()
        for parameter in model.parameters()
        if parameter.requires_grad
    ]
    squared = sum(
        (gradient.double() * gradient.double()).sum() for gradient in gradients
    )
    return gradients, float(torch.sqrt(squared))


def clip_gradient(
    gradients: list[torch.Tensor], norm: float, radius: float | None
) -> tuple[list[torch.Tensor], bool]:
    if radius is None or norm <= radius:
        return gradients, False
    scale = radius / (norm + 1e-12)
    return [gradient.mul_(scale) for gradient in gradients], True


def run_config(config: PilotConfig) -> dict[str, object]:
    set_determinism(SEED)
    assert TRAIN_LABELS is not None
    partitions = dirichlet_partition(TRAIN_LABELS, SEED + 101)
    samplers = [
        ClientSampler(indices, SEED + 10_000 + client)
        for client, indices in enumerate(partitions)
    ]
    model = TwoConvCNN()
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    schedule_rng = random.Random(SEED + 303)
    service_times = [1.0] * 8 + [float(DELAY_FACTOR)] * 8
    worker_available = [0.0] * CLIENTS
    event_queue: list[
        tuple[float, int, int, int, list[torch.Tensor], float, bool]
    ] = []
    sequence = 0
    update_count = 0
    clipped_count = 0
    gradient_norms = []
    staleness = []
    diverged_at_time: float | None = None

    def schedule(worker: int, current_time: float) -> None:
        nonlocal sequence
        gradients, norm = compute_gradient(model, samplers[worker])
        gradients, was_clipped = clip_gradient(
            gradients, norm, config.clipping_radius
        )
        finish = (
            max(current_time, worker_available[worker]) + service_times[worker]
        )
        worker_available[worker] = finish
        heapq.heappush(
            event_queue,
            (
                finish,
                sequence,
                worker,
                update_count,
                gradients,
                norm,
                was_clipped,
            ),
        )
        sequence += 1

    for worker in range(CLIENTS):
        schedule(worker, 0.0)

    initial_accuracy = test_accuracy(model)
    curve = [{"time": 0.0, "oracle_calls": 0, "test_accuracy": initial_accuracy}]
    first_hit_time: float | None = None
    next_evaluation = EVAL_INTERVAL
    last_time = 0.0
    while event_queue:
        (
            current_time,
            _,
            _,
            snapshot_update,
            gradients,
            norm,
            was_clipped,
        ) = heapq.heappop(event_queue)
        if current_time > TIME_CAP:
            break
        if not math.isfinite(norm):
            diverged_at_time = current_time
            break
        with torch.no_grad():
            gradient_index = 0
            for parameter in model.parameters():
                if not parameter.requires_grad:
                    continue
                parameter.add_(
                    gradients[gradient_index], alpha=-config.learning_rate
                )
                gradient_index += 1
        update_count += 1
        last_time = current_time
        clipped_count += int(was_clipped)
        gradient_norms.append(norm)
        staleness.append(update_count - 1 - snapshot_update)
        if current_time >= next_evaluation:
            accuracy = test_accuracy(model)
            curve.append(
                {
                    "time": current_time,
                    "oracle_calls": update_count,
                    "test_accuracy": accuracy,
                }
            )
            while next_evaluation <= current_time:
                next_evaluation += EVAL_INTERVAL
            if accuracy >= TARGET_ACCURACY:
                first_hit_time = current_time
                break
        selected = schedule_rng.randrange(CLIENTS)
        schedule(selected, current_time)

    final_accuracy = curve[-1]["test_accuracy"]
    return {
        "name": config.name,
        "method": "clipped" if config.clipping_radius is not None else "vanilla",
        "learning_rate": config.learning_rate,
        "clipping_radius": config.clipping_radius,
        "parameter_count": parameter_count,
        "batch_size": BATCH_SIZE,
        "time_cap": TIME_CAP,
        "target_accuracy": TARGET_ACCURACY,
        "first_hit_time": first_hit_time,
        "reached_target": first_hit_time is not None,
        "diverged": diverged_at_time is not None,
        "diverged_at_time": diverged_at_time,
        "last_event_time": last_time,
        "oracle_calls": update_count,
        "mean_time_per_oracle_call": last_time / update_count,
        "initial_accuracy": initial_accuracy,
        "final_accuracy": final_accuracy,
        "max_evaluated_accuracy": max(point["test_accuracy"] for point in curve),
        "curve": curve,
        "clipped_updates": clipped_count,
        "clipping_fraction": clipped_count / update_count,
        "gradient_norm_summary": {
            "minimum": min(gradient_norms),
            "median": statistics.median(gradient_norms),
            "maximum": max(gradient_norms),
        },
        "staleness_updates": {
            "minimum": min(staleness),
            "mean": statistics.fmean(staleness),
            "maximum": max(staleness),
        },
    }


def partition_audit(labels: np.ndarray) -> dict[str, object]:
    partitions = dirichlet_partition(labels, SEED + 101)
    concatenated = np.concatenate(partitions)
    counts = []
    distributions = []
    for partition in partitions:
        label_counts = np.bincount(labels[partition], minlength=10)
        counts.append(int(len(partition)))
        distributions.append((label_counts / label_counts.sum()).tolist())
    all_assigned_once = (
        len(concatenated) == len(labels)
        and len(np.unique(concatenated)) == len(labels)
        and int(concatenated.min()) == 0
        and int(concatenated.max()) == len(labels) - 1
    )
    return {
        "alpha": DIRICHLET_ALPHA,
        "clients": CLIENTS,
        "all_examples_assigned_exactly_once": all_assigned_once,
        "client_sizes": counts,
        "minimum_client_size": min(counts),
        "client_label_distributions": distributions,
        "maximum_single_label_share": max(max(row) for row in distributions),
    }


def main() -> int:
    global TRAIN_IMAGES, TRAIN_LABELS, TEST_IMAGES, TEST_LABELS
    started = time.perf_counter()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    data_root = Path(os.environ.get("HF_HOME", "/tmp")) / "openresearch-cifar10"
    datasets.CIFAR10.url = CIFAR_HF_MIRROR
    train = datasets.CIFAR10(root=data_root, train=True, download=True)
    test = datasets.CIFAR10(root=data_root, train=False, download=True)
    TRAIN_IMAGES = train.data
    TRAIN_LABELS = np.asarray(train.targets, dtype=np.int64)
    TEST_IMAGES = test.data
    TEST_LABELS = np.asarray(test.targets, dtype=np.int64)
    audit = partition_audit(TRAIN_LABELS)
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=PROCESS_WORKERS
    ) as executor:
        results = list(executor.map(run_config, CONFIGS))
    no_training_accuracy = results[0]["initial_accuracy"]
    controls = {
        "no_training_target_rejected": no_training_accuracy < TARGET_ACCURACY,
        "no_training_accuracy": no_training_accuracy,
        "clipped_paths_exercised": all(
            result["clipped_updates"] > 0
            for result in results
            if result["method"] == "clipped"
        ),
        "asynchrony_exercised": all(
            result["staleness_updates"]["maximum"] > CLIENTS
            for result in results
        ),
    }
    result = {
        "schema_version": 1,
        "claim_number": 6,
        "route": "real CIFAR-10 protocol calibration pilot",
        "status": "PASS",
        "verdict": "BLOCKED",
        "reason": (
            "This is a preregistered one-seed, D=4, three-configuration pilot "
            "with a 3,200-time-unit cap. It cannot establish the paper's "
            "three-seed full-sweep 1.2x/1.3x claim."
        ),
        "paper_protocol": {
            "dataset": "CIFAR-10",
            "clients": 16,
            "dirichlet_alpha": 0.5,
            "delay_factor": DELAY_FACTOR,
            "target_accuracy": TARGET_ACCURACY,
            "paper_time_cap": 8_000,
            "pilot_time_cap": TIME_CAP,
            "paper_lr_domain": [2.0**exponent for exponent in range(-9, 0)],
            "paper_clipping_radius_domain": [0.5, 1.0, 2.0, 4.0],
            "paper_seeds": 3,
            "pilot_seeds": 1,
        },
        "reconstruction_choices_missing_from_paper": {
            "architecture": "Conv5x5(3,32)-pool-Conv5x5(32,64)-pool-FC512-FC10",
            "batch_size": BATCH_SIZE,
            "preprocessing": "CIFAR channel normalization; no augmentation",
            "evaluation_interval_time_units": EVAL_INTERVAL,
            "partition_implementation": "class-wise Dirichlet allocation",
        },
        "dataset": {
            "train_examples": len(TRAIN_LABELS),
            "test_examples": len(TEST_LABELS),
            "transport_mirror": CIFAR_HF_MIRROR,
        },
        "partition_audit": audit,
        "controls": controls,
        "configurations": results,
        "compute": {
            "estimated_cores": 6,
            "processes": PROCESS_WORKERS,
            "threads_per_process": THREADS_PER_PROCESS,
            "selected_backend": "hf",
            "selected_flavor": "cpu-upgrade",
            "gpu_allowed": False,
        },
        "runtime_seconds": round(time.perf_counter() - started, 6),
    }
    raw = ARTIFACT_DIR / "raw_output.json"
    raw.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"event": "CLAIM6_CIFAR_PILOT_RAW", "result": result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
