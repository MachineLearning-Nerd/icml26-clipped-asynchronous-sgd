"""Trained-checkpoint route for Figure 1's ResNet-18/CIFAR-10 claim."""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms

from reproduction.claims.claim4 import (
    BATCH_SIZE,
    CIFAR_HF_MIRROR,
    REPORTED_THETA,
    SEED,
    THREADS,
    bootstrap_interval,
    cifar_resnet18,
    estimator_controls,
    gradient_error_norms,
    md5,
    reference_gradient,
    set_determinism,
    sha256,
    tail_parameter,
    write_json,
)


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / ".openresearch" / "artifacts" / "claim4_trained"
REFERENCE_BATCHES = 64
ERROR_BATCHES = 128
TRAIN_EPOCHS = 1
PRIMARY_K = int(round(math.sqrt(ERROR_BATCHES)))


def checkpoint_sha256(model: nn.Module) -> str:
    digest = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        digest.update(name.encode("utf-8"))
        digest.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def train_one_epoch(
    model: nn.Module, loader: DataLoader, criterion: nn.Module
) -> dict[str, float | int]:
    optimizer = torch.optim.SGD(
        model.parameters(), lr=0.1, momentum=0.9, weight_decay=5e-4
    )
    model.train()
    loss_sum = 0.0
    correct = 0
    seen = 0
    for inputs, targets in loader:
        optimizer.zero_grad(set_to_none=True)
        logits = model(inputs)
        loss = criterion(logits, targets)
        loss.backward()
        optimizer.step()
        loss_sum += float(loss.detach()) * len(targets)
        correct += int((logits.argmax(dim=1) == targets).sum())
        seen += len(targets)
    return {
        "epochs": TRAIN_EPOCHS,
        "examples": seen,
        "mean_cross_entropy": loss_sum / seen,
        "training_accuracy": correct / seen,
    }


def main() -> int:
    started = time.perf_counter()
    set_determinism(SEED)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    data_root = Path(os.environ.get("HF_HOME", "/tmp")) / "openresearch-cifar10"
    normalize = transforms.Normalize(
        mean=(0.4914, 0.4822, 0.4465),
        std=(0.2470, 0.2435, 0.2616),
    )
    training_transform = transforms.Compose(
        [
            transforms.RandomCrop(32, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            normalize,
        ]
    )
    measurement_transform = transforms.Compose([transforms.ToTensor(), normalize])
    datasets.CIFAR10.url = CIFAR_HF_MIRROR
    training_dataset = datasets.CIFAR10(
        root=data_root, train=True, download=True, transform=training_transform
    )
    measurement_dataset = datasets.CIFAR10(
        root=data_root, train=True, download=False, transform=measurement_transform
    )
    archive_path = data_root / datasets.CIFAR10.filename
    train_generator = torch.Generator().manual_seed(SEED)
    training_loader = DataLoader(
        training_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        generator=train_generator,
        num_workers=0,
    )
    model = cifar_resnet18()
    criterion_mean = nn.CrossEntropyLoss(reduction="mean")
    training = train_one_epoch(model, training_loader, criterion_mean)
    checkpoint_hash = checkpoint_sha256(model)

    split_generator = torch.Generator().manual_seed(SEED + 1)
    permutation = torch.randperm(
        len(measurement_dataset), generator=split_generator
    ).tolist()
    reference_count = REFERENCE_BATCHES * BATCH_SIZE
    error_count = ERROR_BATCHES * BATCH_SIZE
    reference_loader = DataLoader(
        Subset(measurement_dataset, permutation[:reference_count]),
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )
    error_loader = DataLoader(
        Subset(
            measurement_dataset,
            permutation[reference_count : reference_count + error_count],
        ),
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )
    criterion_sum = nn.CrossEntropyLoss(reduction="sum")
    reference, seen = reference_gradient(model, reference_loader, criterion_sum)
    values = np.asarray(
        gradient_error_norms(model, error_loader, criterion_sum, reference),
        dtype=np.float64,
    )
    sensitivity_ks = sorted({8, PRIMARY_K, 16, 24, 32})
    sensitivity = [
        tail_parameter(values, k=k) for k in sensitivity_ks if k < len(values)
    ]
    primary = tail_parameter(values, k=PRIMARY_K)
    interval = bootstrap_interval(values, PRIMARY_K)
    controls = estimator_controls()
    contains_reported = (
        float(interval["low_95"]) <= REPORTED_THETA <= float(interval["high_95"])
    )
    result = {
        "schema_version": 1,
        "claim_number": 4,
        "claim": "Figure 1 empirical ResNet-18/CIFAR-10 tail estimate theta=2.71",
        "verdict": "BLOCKED",
        "reason": (
            "This route addresses the paper's in-training wording with a real "
            "trained checkpoint, but the paper does not identify its checkpoint, "
            "optimizer, preprocessing, reference-gradient protocol, n, or k."
        ),
        "reported_theta": REPORTED_THETA,
        "reported_theta_in_bootstrap_interval": contains_reported,
        "primary_estimate": primary,
        "bootstrap": interval,
        "tail_fraction_sensitivity": sensitivity,
        "gradient_error_norms": values.tolist(),
        "negative_control": controls,
        "dataset": {
            "name": "torchvision CIFAR10 train",
            "size": len(measurement_dataset),
            "reference_examples": seen,
            "error_examples": error_count,
            "batch_size": BATCH_SIZE,
            "archive_md5": md5(archive_path),
            "transport_mirror": CIFAR_HF_MIRROR,
        },
        "model": {
            "name": "torchvision ResNet-18 with CIFAR 3x3 stem and no max-pool",
            "parameter_count": sum(p.numel() for p in model.parameters()),
            "checkpoint": "after one complete deterministic CIFAR-10 epoch",
            "checkpoint_sha256": checkpoint_hash,
            "measurement_mode": "train (batch-normalization batch statistics)",
        },
        "training": training,
        "estimator": {
            "source": "Vladimirova et al. (2020), Section 4",
            "regression_response": "log Y_(n-i+1,n)",
            "regression_predictor": "log log(n/i)",
            "primary_k_rule": "round(sqrt(n))",
            "primary_k": PRIMARY_K,
        },
        "seed": SEED,
        "threads": THREADS,
        "runtime_seconds": round(time.perf_counter() - started, 6),
    }
    raw_path = ARTIFACT_DIR / "raw_output.json"
    control_path = ARTIFACT_DIR / "negative_control.json"
    write_json(raw_path, result)
    write_json(control_path, controls)
    print(
        json.dumps(
            {
                "event": "CLAIM4_TRAINED_RAW_EVIDENCE",
                "raw_output_sha256": sha256(raw_path),
                "negative_control_sha256": sha256(control_path),
                "result": result,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
