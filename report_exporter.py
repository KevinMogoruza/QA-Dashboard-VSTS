from datetime import datetime
from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd


REPORT_DIR = Path(__file__).resolve().parent / "reports"


def _draw_kpis(ax, metrics):
    ax.axis("off")
    ax.set_facecolor("#0b1220")

    positions = [0.03, 0.225, 0.42, 0.615, 0.81]
    colors = ["#e5e7eb", "#22c55e", "#ef4444", "#f59e0b", "#38bdf8"]

    for index, metric in enumerate(metrics):
        x = positions[index]
        rect = plt.Rectangle(
            (x, 0.18),
            0.16,
            0.64,
            facecolor="#111827",
            edgecolor="#1f2937",
            linewidth=1.2,
            transform=ax.transAxes,
        )
        ax.add_patch(rect)
        ax.text(
            x + 0.08,
            0.57,
            str(metric["value"]),
            ha="center",
            va="center",
            color=colors[index],
            fontsize=18,
            fontweight="bold",
            transform=ax.transAxes,
        )
        ax.text(
            x + 0.08,
            0.34,
            metric["label"],
            ha="center",
            va="center",
            color="#94a3b8",
            fontsize=9,
            transform=ax.transAxes,
        )


def _draw_table(ax, data, title, max_rows=18):
    ax.axis("off")
    ax.set_title(title, loc="left", color="#e5e7eb", fontsize=14, pad=10)
    ax.set_facecolor("#0b1220")

    if data.empty:
        ax.text(0.02, 0.85, "No data available", color="#94a3b8", fontsize=11)
        return

    display = data.head(max_rows).copy()
    table = ax.table(
        cellText=display.astype(str).values,
        colLabels=display.columns,
        cellLoc="left",
        colLoc="left",
        loc="upper left",
        bbox=[0, 0, 1, 0.88],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1, 1.25)

    for (row, _), cell in table.get_celld().items():
        cell.set_edgecolor("#1f2937")
        if row == 0:
            cell.set_facecolor("#1f2937")
            cell.set_text_props(color="#e5e7eb", weight="bold")
        else:
            cell.set_facecolor("#111827")
            cell.set_text_props(color="#e5e7eb")

    if len(data) > max_rows:
        ax.text(
            0,
            -0.05,
            f"Showing first {max_rows} of {len(data)} rows.",
            color="#94a3b8",
            fontsize=8,
            transform=ax.transAxes,
        )


def _wrap_titles(df, column="Title", width=70):
    if df.empty or column not in df.columns:
        return df

    wrapped = df.copy()
    wrapped[column] = wrapped[column].astype(str).map(
        lambda value: "\n".join(textwrap.wrap(value, width=width))
    )
    return wrapped


def generate_dashboard_pdf(project, plan_id, df, bugs_df):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    pdf_path = REPORT_DIR / f"QA_Report_{today}.pdf"

    total = int(df["Test Points"].sum()) if not df.empty else 0
    passed = int(df["passed"].sum()) if not df.empty else 0
    failed = int(df["failed"].sum()) if not df.empty else 0
    notrun = int(df["notrun"].sum()) if not df.empty else 0
    executed = passed + failed
    run_rate = round((executed / total) * 100, 1) if total else 0

    if bugs_df.empty:
        state_counts = pd.Series(dtype="int64")
        priority_counts = pd.Series(dtype="int64")
    else:
        state_counts = bugs_df["State"].value_counts()
        priority_counts = bugs_df["Priority"].astype(str).value_counts().sort_index()

    plt.rcParams.update({
        "figure.facecolor": "#0b1220",
        "axes.facecolor": "#0b1220",
        "savefig.facecolor": "#0b1220",
        "text.color": "#e5e7eb",
        "axes.labelcolor": "#e5e7eb",
        "xtick.color": "#e5e7eb",
        "ytick.color": "#e5e7eb",
    })

    with PdfPages(pdf_path) as pdf:
        fig = plt.figure(figsize=(11.69, 8.27))
        fig.patch.set_facecolor("#0b1220")
        grid = fig.add_gridspec(3, 2, height_ratios=[0.45, 0.75, 1.8])

        title_ax = fig.add_subplot(grid[0, :])
        title_ax.axis("off")
        title_ax.text(
            0,
            0.75,
            "QA REPORT",
            fontsize=24,
            fontweight="bold",
            color="#e5e7eb",
        )
        title_ax.text(
            0,
            0.35,
            f"{project} | Test Plan {plan_id} | {today}",
            fontsize=11,
            color="#94a3b8",
        )

        kpi_ax = fig.add_subplot(grid[1, :])
        _draw_kpis(kpi_ax, [
            {"label": "TOTAL", "value": total},
            {"label": "PASSED", "value": passed},
            {"label": "FAILED", "value": failed},
            {"label": "NOT RUN", "value": notrun},
            {"label": "RUN RATE", "value": f"{run_rate}%"},
        ])

        execution_ax = fig.add_subplot(grid[2, 0])
        execution_ax.set_title("Execution Overview", color="#e5e7eb", fontsize=14)
        execution_values = [passed, failed, notrun]
        if sum(execution_values):
            execution_ax.pie(
                execution_values,
                labels=[f"Passed ({passed})", f"Failed ({failed})", f"Not Run ({notrun})"],
                colors=["#22c55e", "#ef4444", "#f59e0b"],
                startangle=90,
                textprops={"color": "#e5e7eb", "fontsize": 9},
            )
        else:
            execution_ax.text(0.5, 0.5, "No execution data", ha="center", color="#94a3b8")

        bugs_ax = fig.add_subplot(grid[2, 1])
        bugs_ax.set_title("Bug Status", color="#e5e7eb", fontsize=14)
        if not state_counts.empty:
            bugs_ax.pie(
                state_counts.values,
                labels=[f"{state} ({count})" for state, count in state_counts.items()],
                colors=["#22c55e", "#ef4444", "#f59e0b", "#3b82f6", "#8b5cf6", "#06b6d4"],
                startangle=90,
                textprops={"color": "#e5e7eb", "fontsize": 9},
            )
        else:
            bugs_ax.text(0.5, 0.5, "No bug data", ha="center", color="#94a3b8")

        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        suite_df = df.copy()
        suite_df.index = range(1, len(suite_df) + 1)
        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        fig.patch.set_facecolor("#0b1220")
        _draw_table(ax, suite_df, "Test Suites Summary", max_rows=24)
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        fig = plt.figure(figsize=(11.69, 8.27))
        fig.patch.set_facecolor("#0b1220")
        grid = fig.add_gridspec(2, 1, height_ratios=[0.9, 2])

        priority_ax = fig.add_subplot(grid[0])
        priority_ax.set_title("Bug Priority", loc="left", color="#e5e7eb", fontsize=14)
        if not priority_counts.empty:
            priority_ax.bar(
                [f"P{priority}" for priority in priority_counts.index],
                priority_counts.values,
                color="#38bdf8",
            )
            priority_ax.grid(axis="y", color="#1f2937")
        else:
            priority_ax.axis("off")
            priority_ax.text(0.02, 0.6, "No priority data", color="#94a3b8")

        bugs_table_ax = fig.add_subplot(grid[1])
        bugs_display = _wrap_titles(bugs_df.copy())
        bugs_display.index = range(1, len(bugs_display) + 1)
        _draw_table(bugs_table_ax, bugs_display, "Bug Detail", max_rows=16)
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

    return pdf_path
