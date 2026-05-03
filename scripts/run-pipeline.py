from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PREPROCESSED_DIR = DATA_DIR / "preprocessed"
RESULTS_DIR = ROOT / "results"
TABLES_DIR = RESULTS_DIR / "tables"
FIGURES_DIR = RESULTS_DIR / "figures"
MPLCONFIG_DIR = ROOT / ".cache" / "matplotlib"


TABLE_OUTPUTS = [
    "efficiencies.csv",
    "ahp_weights_cr.csv",
    "efficient_topsis_ranking.csv",
]

FIGURE_OUTPUTS = [
    "mcdm_comparison_line.png",
    "mcdm_comparison_bar.png",
    "mcdm_comparison_heatmap.png",
    "mcdm_comparison_radar.png",
    "mcdm_comparison_boxplot.png",
]


def ensure_directories() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    MPLCONFIG_DIR.mkdir(parents=True, exist_ok=True)


def copy_required_inputs() -> None:
    required_inputs = {
        PREPROCESSED_DIR / "First-sample.csv": DATA_DIR / "First-sample.csv",
        TABLES_DIR / "all-method-score.csv": DATA_DIR / "all-method-score.csv",
    }

    missing = [str(source.relative_to(ROOT)) for source in required_inputs if not source.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing required pipeline input(s): " + ", ".join(missing)
        )

    for source, destination in required_inputs.items():
        shutil.copy2(source, destination)


def run_script(script_path: Path) -> None:
    print(f"\n==> Running {script_path.relative_to(ROOT)}", flush=True)
    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"
    env["MPLCONFIGDIR"] = str(MPLCONFIG_DIR)

    subprocess.run(
        [sys.executable, str(script_path)],
        cwd=ROOT,
        env=env,
        check=True,
    )


def collect_outputs() -> None:
    for file_name in TABLE_OUTPUTS:
        source = DATA_DIR / file_name
        if source.exists():
            shutil.copy2(source, TABLES_DIR / file_name)

    for file_name in FIGURE_OUTPUTS:
        source = ROOT / file_name
        if source.exists():
            shutil.move(str(source), FIGURES_DIR / file_name)


def main() -> None:
    ensure_directories()
    copy_required_inputs()

    run_script(ROOT / "src" / "mcdm" / "dea-ahp-topsis.py")
    run_script(ROOT / "src" / "visualization" / "mcdm-graphs.py")

    collect_outputs()

    print("\nPipeline complete.")
    print(f"Tables:  {TABLES_DIR.relative_to(ROOT)}")
    print(f"Figures: {FIGURES_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
