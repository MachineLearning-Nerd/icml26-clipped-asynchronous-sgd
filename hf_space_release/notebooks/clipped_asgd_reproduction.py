import marimo

__generated_with = "0.23.14"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt

    return mo, plt


@app.cell
def _(mo):
    mo.md(r"""
    # Clipping and asynchronous SGD: evidence first

    This notebook is a self-contained guide to the accepted evidence. It
    embeds the small numerical results; no training run is required.
    """)
    return


@app.cell
def _(plt):
    labels = ["C1", "C2", "C3", "C4", "C5", "C6"]
    possible = [2, 2, 2, 0, 2, 1]
    colors = ["#2a9d8f", "#2a9d8f", "#e76f51", "#6c757d", "#e76f51", "#6c757d"]
    figure, axis = plt.subplots(figsize=(8, 3))
    axis.bar(labels, possible, color=colors)
    axis.set_ylim(0, 2.25)
    axis.set_ylabel("Best-supported possible points")
    axis.set_title("VERIFIED / FALSIFIED / BLOCKED evidence")
    figure
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Why clipping removes the maximum-delay symbol

    At most \(\tau_C\) clipped gradients are outstanding. Each update has
    norm at most \(\eta c\), so the virtual-iterate gap is bounded by
    \(\eta c\tau_C\), regardless of the oldest gradient's delay. The checked
    proof then yields

    \[
    \widetilde O\!\left(
    \frac{\sigma^2}{\epsilon^4}+
    \frac{\sigma\tau_C}{\epsilon^3}+
    \frac{\tau_C}{\epsilon^2}\right).
    \]

    The heterogeneous certificate replaces the first two factors by
    \(\sigma^2+\zeta^2\) and \(\sigma+\zeta\).
    """)
    return


@app.cell
def _(mo):
    validation = {
        "D4_speedup": 1.0227272727,
        "D4_combined_95": [0.9283383346, 1.1206521739],
        "paper_D4": 1.2,
        "D8_censored_clipped_seed": 20260731,
    }
    mo.md(
        f"""
        ## A real-data diagnostic

        The label-skew CIFAR-10 validation produced a D4 speedup of
        **{validation["D4_speedup"]:.3f}x**, with combined 95% interval
        **[{validation["D4_combined_95"][0]:.3f},
        {validation["D4_combined_95"][1]:.3f}]**. It includes no effect and
        excludes the paper's 1.2x value. D8 was censored for clipped seed
        `{validation["D8_censored_clipped_seed"]}`.

        This is a discrepancy, not a historical falsification: the original
        CNN, seeds, scheduler details, cadence, and aggregation are unavailable.
        """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Final assessment

    - Claims 1–2: **VERIFIED**
    - Claim 3: **FALSIFIED** by pre-existing 2021 high-probability ASGD
    - Claim 4: **BLOCKED** on the unidentified source checkpoint/protocol
    - Claim 5: **FALSIFIED (MEDIUM)** under the carried Vanilla comparator
    - Claim 6: **BLOCKED** despite a real-data discrepancy

    The live score is still 4/12. The forecast is 6–9/12, pending the judge.
    """)
    return


if __name__ == "__main__":
    app.run()
