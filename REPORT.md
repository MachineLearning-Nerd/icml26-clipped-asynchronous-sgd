# Reproduction report

## Result

This repository supports the two expectation-rate claims through an independently reconstructed symbolic DAG. It does not support a blanket “all claims reproduced” conclusion: C3 is compound, with its broad novelty conjunct falsified and its narrower theta-rate blocked; C5 is comparator-dependent and falsified under the carried Vanilla-ASGD reading; C4 and C6 remain blocked by missing historical protocol artifacts.

## What the paper does

The paper studies clipped asynchronous SGD under delays and heavy-tailed noise. It proposes clipping as a way to remove maximum-delay dependence from expectation-rate oracle complexity, extends the analysis to heterogeneous workers, and reports high-probability and CIFAR/Shakespeare experiments.

## Evidence highlights

- C1/C2 expectation-rate proof DAG passes its constructive obligations and controls.
- Cohen et al. (NeurIPS 2021) predates the paper with an arbitrary-confidence asynchronous optimization result, falsifying the unrestricted “first” novelty conjunct.
- C4 initialized and trained reconstructions produce theta estimates `0.0789` and `0.2246`, but cannot identify the authors’ historical checkpoint/protocol.
- C5’s source audit finds Vanilla Shakespeare D4 `1.8×` versus the imported `2.0–2.2×` range; Delay-adaptive ASGD yields `2.1×/2.2×`, so comparator wording matters.
- C6’s independent D4 validation gives `1.0227×` with interval `[0.9283,1.1207]`; D8 has a censored clipped seed, and exact historical protocol fields remain unavailable.

## Reproduction boundary

The historical live score is `4/12`. The `6–9/12` values are forecasts only. No current judge score is asserted, and the repository does not claim author endorsement.
