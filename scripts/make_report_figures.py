"""Generate presentation figures from committed, accepted evidence."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


OUT = Path(__file__).resolve().parents[1] / "reports" / "clipping-asgd" / "images"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"figure.dpi": 150, "font.size": 10})


def save(fig: plt.Figure, name: str) -> None:
    fig.tight_layout()
    fig.savefig(OUT / name, bbox_inches="tight")
    plt.close(fig)


def headline() -> None:
    labels = ["C1", "C2", "C3", "C4", "C5", "C6"]
    values = [2, 2, 2, 0, 2, 1]
    colors = ["#2a9d8f", "#2a9d8f", "#e76f51", "#6c757d", "#e76f51", "#6c757d"]
    fig, ax = plt.subplots(figsize=(8, 3.3))
    ax.bar(labels, values, color=colors)
    ax.set_ylim(0, 2.25)
    ax.set_ylabel("Best-supported possible points")
    ax.set_title("Current evidence: verified, falsified, and blocked claims")
    for index, (value, status) in enumerate(
        zip(values, ["VERIFIED", "VERIFIED", "FALSIFIED", "BLOCKED", "FALSIFIED", "BLOCKED"])
    ):
        ax.text(index, value + 0.07, status, ha="center", fontsize=8)
    ax.text(
        5.45,
        2.05,
        "Forecast 6–9/12\nLive judge still 4/12",
        ha="right",
        va="top",
        bbox={"facecolor": "white", "edgecolor": "#555"},
    )
    save(fig, "headline-status.png")


def complexity() -> None:
    fig, ax = plt.subplots(figsize=(8, 3.5))
    terms = [r"$\sigma^2/\epsilon^4$", r"$\sigma\tau_C/\epsilon^3$", r"$\tau_C/\epsilon^2$"]
    powers = [4, 3, 2]
    ax.barh(terms, powers, color=["#264653", "#2a9d8f", "#e9c46a"])
    ax.set_xlabel("inverse-accuracy exponent")
    ax.set_title("Claims 1–2 certificate: exact terms, no maximum-delay symbol")
    ax.text(3.95, 2.35, r"$\tau_{\max}$ absent", ha="right", color="#b02a37", weight="bold")
    save(fig, "complexity-certificate.png")


def prior_timeline() -> None:
    fig, ax = plt.subplots(figsize=(8, 2.5))
    ax.hlines(0, 2020.5, 2026.7, color="#555")
    ax.scatter([2021.47, 2026.45], [0, 0], s=[120, 120], color=["#e76f51", "#264653"])
    ax.text(2021.47, 0.12, "Picky SGD\nhigh probability via restarts", ha="center")
    ax.text(2026.45, -0.18, "Target paper\nclaims first result", ha="center")
    ax.set_xlim(2020.5, 2026.7)
    ax.set_ylim(-0.35, 0.35)
    ax.set_yticks([])
    ax.set_xlabel("year")
    ax.set_title("Claim 3 novelty falsification: primary result predates target by five years")
    save(fig, "prior-art-timeline.png")


def theta_routes() -> None:
    labels = ["initial", "trained", "max tail audit", "paper"]
    values = [0.078919, 0.224648, 0.234507, 2.71]
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.bar(labels, values, color=["#457b9d", "#457b9d", "#457b9d", "#e63946"])
    ax.set_ylabel(r"fitted $\theta$")
    ax.set_title("Claim 4: real reconstructions disagree, but source protocol is unidentified")
    save(fig, "theta-routes.png")


def claim6_interval() -> None:
    fig, ax = plt.subplots(figsize=(8, 3.2))
    point = 1.022727
    low, high = 0.928338, 1.120652
    ax.errorbar([point], [0], xerr=[[point - low], [high - point]], fmt="o", capsize=7, color="#264653")
    ax.axvline(1.0, color="#555", linestyle="--", label="no effect")
    ax.axvline(1.2, color="#e63946", linestyle="-", label="paper D4 value")
    ax.set_xlim(0.88, 1.25)
    ax.set_yticks([])
    ax.set_xlabel("Vanilla / Clipped first-hit time")
    ax.set_title("Claim 6 D4 validation: 95% interval includes no effect and excludes 1.2×")
    ax.legend(loc="upper right")
    save(fig, "claim6-validation.png")


def main() -> None:
    headline()
    complexity()
    prior_timeline()
    theta_routes()
    claim6_interval()


if __name__ == "__main__":
    main()
