"""Real-data pilot for the CIFAR-10 ResNet-18 gradient-noise claim.

This is deliberately a calibration run. The paper does not report enough
protocol details to turn a numerical mismatch into a falsification.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, models, transforms


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / ".openresearch" / "artifacts" / "claim4"
SEED = 20260728
THREADS = 8
BATCH_SIZE = 128
REFERENCE_BATCHES = 16
ERROR_BATCHES = 24
BOOTSTRAP_REPLICATES = 400
PRIMARY_TAIL_FRACTION = 1 / 3
REPORTED_THETA = 2.71
CIFAR_HF_MIRROR = (
    "https://huggingface.co/datasets/VerisimilitudeX/cifar10/resolve/main/"
    "cifar-10-python.tar.gz"
)


def set_determinism(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(THREADS)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def md5(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cifar_resnet18() -> nn.Module:
    model = models.resnet18(weights=None, num_classes=10)
    model.conv1 = nn.Conv2d(
        3, 64, kernel_size=3, stride=1, padding=1, bias=False
    )
    model.maxpool = nn.Identity()
    return model


def tail_parameter(values: np.ndarray, k: int) -> dict[str, float | int]:
    if values.ndim != 1 or len(values) < 8:
        raise ValueError("tail estimator requires at least eight scalar observations")
    if not 3 <= k < len(values):
        raise ValueError("k must select at least three but not all observations")
    descending = np.sort(values)[::-1]
    ranks = np.arange(1, k + 1, dtype=np.float64)
    predictor = np.log(np.log(len(values) / ranks))
    response = np.log(descending[:k])
    slope, intercept = np.polyfit(predictor, response, deg=1)
    fitted = slope * predictor + intercept
    residual = response - fitted
    total = response - response.mean()
    r_squared = 1.0 - float(residual @ residual) / float(total @ total)
    return {
        "n": int(len(values)),
        "k": int(k),
        "theta": float(slope),
        "intercept": float(intercept),
        "r_squared": r_squared,
    }


def bootstrap_interval(values: np.ndarray, k: int) -> dict[str, float | int]:
    rng = np.random.default_rng(SEED + 17)
    estimates = []
    for _ in range(BOOTSTRAP_REPLICATES):
        sample = rng.choice(values, size=len(values), replace=True)
        estimates.append(float(tail_parameter(sample, k)["theta"]))
    low, high = np.quantile(np.asarray(estimates), [0.025, 0.975])
    return {
        "replicates": BOOTSTRAP_REPLICATES,
        "low_95": float(low),
        "high_95": float(high),
    }


def estimator_controls() -> dict[str, object]:
    rng = np.random.default_rng(SEED + 29)
    controls = []
    all_pass = True
    for expected in (0.5, 1.0, 2.71):
        # NumPy's Weibull shape is the reciprocal of the paper's theta.
        sample = rng.weibull(1.0 / expected, size=100_000)
        observed = tail_parameter(sample, k=1_000)
        absolute_error = abs(float(observed["theta"]) - expected)
        passed = absolute_error <= 0.18
        all_pass = all_pass and passed
        controls.append(
            {
                "distribution": "numpy Weibull",
                "expected_theta": expected,
                "observed": observed,
                "absolute_error": absolute_error,
                "tolerance": 0.18,
                "pass": passed,
            }
        )
    target_case = controls[-1]
    wrong_convention = 1.0 / float(target_case["observed"]["theta"])
    negative_case = {
        "name": "reciprocal shape-parameter convention",
        "observed_theta_if_wrong": wrong_convention,
        "expected_theta": 2.71,
        "tolerance": 0.18,
        "passes_claim_threshold": abs(wrong_convention - 2.71) <= 0.18,
        "rejected_as_intended": abs(wrong_convention - 2.71) > 0.18,
    }
    return {
        "name": "known-theta estimator calibration",
        "pass": all_pass and bool(negative_case["rejected_as_intended"]),
        "cases": controls,
        "negative_case": negative_case,
    }


def reference_gradient(
    model: nn.Module, loader: DataLoader, criterion: nn.Module
) -> tuple[list[torch.Tensor], int]:
    model.train()
    model.zero_grad(set_to_none=True)
    seen = 0
    for inputs, targets in loader:
        loss = criterion(model(inputs), targets)
        loss.backward()
        seen += len(targets)
    reference = [
        parameter.grad.detach().clone().div_(seen)
        for parameter in model.parameters()
        if parameter.requires_grad
    ]
    model.zero_grad(set_to_none=True)
    return reference, seen


def gradient_error_norms(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    reference: list[torch.Tensor],
) -> list[float]:
    values: list[float] = []
    model.train()
    for inputs, targets in loader:
        model.zero_grad(set_to_none=True)
        (criterion(model(inputs), targets) / len(targets)).backward()
        squared = torch.zeros((), dtype=torch.float64)
        ref_index = 0
        for parameter in model.parameters():
            if not parameter.requires_grad:
                continue
            difference = parameter.grad.detach() - reference[ref_index]
            squared += torch.sum(difference.double() * difference.double())
            ref_index += 1
        values.append(float(torch.sqrt(squared)))
    return values


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    started = time.perf_counter()
    set_determinism(SEED)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    data_root = Path(os.environ.get("HF_HOME", "/tmp")) / "openresearch-cifar10"
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(
                mean=(0.4914, 0.4822, 0.4465),
                std=(0.2470, 0.2435, 0.2616),
            ),
        ]
    )
    datasets.CIFAR10.url = CIFAR_HF_MIRROR
    dataset = datasets.CIFAR10(
        root=data_root, train=True, download=True, transform=transform
    )
    archive_path = data_root / datasets.CIFAR10.filename
    generator = torch.Generator().manual_seed(SEED)
    permutation = torch.randperm(len(dataset), generator=generator).tolist()
    reference_count = REFERENCE_BATCHES * BATCH_SIZE
    error_count = ERROR_BATCHES * BATCH_SIZE
    reference_loader = DataLoader(
        Subset(dataset, permutation[:reference_count]),
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )
    error_loader = DataLoader(
        Subset(dataset, permutation[reference_count : reference_count + error_count]),
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )
    model = cifar_resnet18()
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    criterion = nn.CrossEntropyLoss(reduction="sum")
    reference, seen = reference_gradient(model, reference_loader, criterion)
    values = np.asarray(
        gradient_error_norms(model, error_loader, criterion, reference),
        dtype=np.float64,
    )
    primary_k = max(3, int(round(len(values) * PRIMARY_TAIL_FRACTION)))
    sensitivity = [
        tail_parameter(values, k=k)
        for k in sorted({6, 8, 10, 12, primary_k})
        if k < len(values)
    ]
    primary = tail_parameter(values, k=primary_k)
    interval = bootstrap_interval(values, primary_k)
    controls = estimator_controls()
    contains_reported = (
        float(interval["low_95"]) <= REPORTED_THETA <= float(interval["high_95"])
    )
    result = {
        "schema_version": 1,
        "claim": "Figure 1 empirical ResNet-18/CIFAR-10 tail estimate theta=2.71",
        "claim_number": 4,
        "verdict": "BLOCKED",
        "reason": (
            "The paper omits the training checkpoint, batch size, preprocessing, "
            "sample count, reference-gradient construction, and tail fraction k/n. "
            "This preregistered pilot is a real-data protocol calibration, not an "
            "assumption-identical verification or falsification."
        ),
        "reported_theta": REPORTED_THETA,
        "reported_theta_in_pilot_bootstrap_interval": contains_reported,
        "primary_estimate": primary,
        "bootstrap": interval,
        "tail_fraction_sensitivity": sensitivity,
        "gradient_error_norms": values.tolist(),
        "negative_control": controls,
        "dataset": {
            "name": "torchvision CIFAR10 train",
            "size": len(dataset),
            "reference_examples": seen,
            "error_examples": error_count,
            "batch_size": BATCH_SIZE,
            "downloaded_archive_md5_documented_by_torchvision": "c58f30108f718f92721af3b95e74349a",
            "downloaded_archive_md5_observed": md5(archive_path),
            "transport_mirror": CIFAR_HF_MIRROR,
        },
        "model": {
            "name": "torchvision ResNet-18 with CIFAR 3x3 stem and no max-pool",
            "parameter_count": parameter_count,
            "checkpoint": "deterministic Kaiming initialization; no training",
        },
        "estimator": {
            "source": "Vladimirova et al. (2020), Section 4 tail parameter estimation",
            "regression_response": "log Y_(n-i+1,n)",
            "regression_predictor": "log log(n/i)",
            "primary_tail_fraction": PRIMARY_TAIL_FRACTION,
        },
        "seed": SEED,
        "threads": THREADS,
        "runtime_seconds": round(time.perf_counter() - started, 6),
    }
    raw_path = ARTIFACT_DIR / "raw_output.json"
    control_path = ARTIFACT_DIR / "negative_control.json"
    write_json(raw_path, result)
    write_json(control_path, controls)
    envelope = {
        "event": "CLAIM4_RAW_EVIDENCE",
        "raw_output_sha256": sha256(raw_path),
        "negative_control_sha256": sha256(control_path),
        "result": result,
    }
    print(json.dumps(envelope, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
