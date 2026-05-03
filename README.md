# OSS-MCDM

> Solar photovoltaic site selection for Amritsar, Punjab using a hybrid DEA-AHP-TOPSIS decision-support pipeline.

`OSS-MCDM` combines geospatial, meteorological, environmental, and solar irradiance data to rank candidate solar PV installation sites. The workflow is designed around interpretable multi-criteria decision-making (MCDM), with generated tables and figures for analysis and reporting.

## At A Glance

| Area | Details |
| --- | --- |
| Study region | Amritsar, Punjab, India |
| Main task | Rank candidate coordinates for solar PV site suitability |
| Core model | DEA-AHP-TOPSIS |
| Comparison models | MARCOS, VIKOR, WASPAS |
| Primary runner | `python scripts/run-pipeline.py` |
| Main outputs | CSV rankings in `results/tables/`, plots in `results/figures/` |

## Contents

- [Project Goal](#project-goal)
- [Methodology](#methodology)
- [Repository Structure](#repository-structure)
- [Setup](#setup)
- [How To Run](#how-to-run)
- [Inputs And Outputs](#inputs-and-outputs)
- [Key Scripts](#key-scripts)
- [Notes And Limitations](#notes-and-limitations)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)

## Project Goal

Solar PV site selection is a multi-factor decision problem. A strong location should maximize solar potential while balancing environmental and meteorological constraints.

This repository evaluates candidate sites using:

| Category | Criteria |
| --- | --- |
| Solar irradiance | `DHI`, `DNI`, `GHI` |
| Meteorology | `RELATIVE_HUMIDITY`, `WIND_SPEED_10m` |
| Environment | `NDVI`, `LST` |
| Spatial context | `Latitude`, `Longitude`, district/sub-district metadata |

The current dataset focuses on Amritsar-area administrative regions, including Amritsar I, Amritsar II, Baba Bakala, and Ajnala.

## Methodology

The main decision workflow follows a sequential hybrid MCDM design:

```text
Candidate coordinates
        |
        v
DEA efficiency screening
        |
        v
AHP criteria weighting
        |
        v
TOPSIS final ranking
        |
        v
Tables, rankings, and visualizations
```

### Stage 1: DEA Screening

Data Envelopment Analysis treats each coordinate as a decision-making unit (DMU). It compares how well each location converts less-desirable input factors into desirable solar output factors.

| DEA role | Criteria |
| --- | --- |
| Inputs | `RELATIVE_HUMIDITY`, `WIND_SPEED_10m`, `NDVI`, `LST` |
| Outputs | `DHI`, `DNI`, `GHI` |
| Output columns | `CRS`, `VRS`, `SE`, `Fully Efficient` |

### Stage 2: AHP Weighting

The Analytic Hierarchy Process uses a pairwise comparison matrix to estimate the relative importance of each criterion. The script also calculates a consistency ratio (`CR`) to validate the pairwise judgments.

### Stage 3: TOPSIS Ranking

TOPSIS ranks the DEA-filtered efficient sites by measuring each location's closeness to an ideal solution. Higher TOPSIS scores indicate better suitability.

The repository also includes comparative MCDM scripts for MARCOS, VIKOR, and WASPAS.

## Repository Structure

```text
.
├── data/
│   ├── raw/                  # Raw geospatial and environmental data
│   ├── preprocessed/         # Cleaned/prepared model inputs
│   └── *.csv, *.png          # Pipeline working copies and generated artifacts
├── gee-data-scripts/         # Google Earth Engine scripts for source data extraction
├── results/
│   ├── figures/              # Final generated plots
│   └── tables/               # Final generated CSV outputs
├── scripts/
│   └── run-pipeline.py       # One-command pipeline runner
├── src/
│   ├── geo/                  # Geocoding and district/sub-district scripts
│   ├── mcdm/                 # DEA, AHP, TOPSIS, MARCOS, VIKOR, WASPAS models
│   ├── models/               # ML helper scripts, currently XGBoost for LST filling
│   ├── preprocessing/        # Data cleaning/preprocessing scripts
│   └── visualization/        # Plot generation scripts
├── requirements.txt          # Python dependencies
└── README.md
```

## Setup

Use Python 3.10 or newer. This project has been run with Python 3.13.2.

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Dependencies currently listed in `requirements.txt`:

| Package | Used for |
| --- | --- |
| `pandas`, `numpy` | Data manipulation and numerical computation |
| `matplotlib`, `seaborn` | Plot generation |
| `geopandas` | Geospatial data workflows |
| `opencage` | Geocoding support |
| `pyDecision` | MCDM algorithm support |
| `pulp` | DEA optimization |
| `tabulate` | Console table output |
| `xgboost`, `scikit-learn` | ML helper workflows |

## How To Run

Run the full DEA-AHP-TOPSIS and visualization pipeline:

```bash
source .venv/bin/activate
python scripts/run-pipeline.py
```

The runner performs the end-to-end workflow:

| Step | Action |
| --- | --- |
| 1 | Creates required output directories |
| 2 | Copies `data/preprocessed/First-sample.csv` to `data/First-sample.csv` for script compatibility |
| 3 | Copies `results/tables/all-method-score.csv` to `data/all-method-score.csv` for graph generation |
| 4 | Runs `src/mcdm/dea-ahp-topsis.py` |
| 5 | Runs `src/visualization/mcdm-graphs.py` |
| 6 | Copies generated CSV outputs into `results/tables/` |
| 7 | Moves generated plots into `results/figures/` |

## Inputs And Outputs

### Main Input

Primary model input:

```text
data/preprocessed/First-sample.csv
```

Expected columns:

| Column | Meaning |
| --- | --- |
| `City`, `Districts` | Location metadata |
| `Date` | Observation date |
| `Latitude`, `Longitude` | Candidate coordinate |
| `Key` | Coordinate/date key |
| `DHI`, `DNI`, `GHI` | Solar irradiance criteria |
| `RELATIVE_HUMIDITY` | Humidity criterion |
| `WIND_SPEED_10m` | Wind-speed criterion |
| `NDVI` | Vegetation criterion |
| `LST` | Land surface temperature criterion |

Comparison graph input:

```text
results/tables/all-method-score.csv
```

Expected score columns:

```text
TOPSIS_Score
MARCOS_Score
VIKOR_Score
WASPAS_Score
```

### Main Outputs

Generated tables:

| File | Description |
| --- | --- |
| `results/tables/efficiencies.csv` | DEA CRS, VRS, scale efficiency, and efficiency labels |
| `results/tables/ahp_weights_cr.csv` | AHP criteria weights and consistency ratio |
| `results/tables/efficient_topsis_ranking.csv` | Final TOPSIS ranking for fully efficient locations |

Generated figures:

| File | Description |
| --- | --- |
| `results/figures/mcdm_comparison_line.png` | Score comparison line plot |
| `results/figures/mcdm_comparison_bar.png` | Grouped method comparison bar plot |
| `results/figures/mcdm_comparison_heatmap.png` | District/method heatmap |
| `results/figures/mcdm_comparison_radar.png` | Radar chart for the top district |
| `results/figures/mcdm_comparison_boxplot.png` | Distribution of normalized method scores |

## Key Scripts

| Path | Purpose |
| --- | --- |
| `scripts/run-pipeline.py` | Runs the current end-to-end workflow |
| `src/mcdm/dea-ahp-topsis.py` | Primary DEA-AHP-TOPSIS model |
| `src/mcdm/dea-ahp-marcos.py` | DEA-AHP-MARCOS comparison model |
| `src/mcdm/dea-ahp-vikor.py` | DEA-AHP-VIKOR comparison model |
| `src/mcdm/dea-ahp-waspas.py` | DEA-AHP-WASPAS comparison model |
| `src/mcdm/ahp-entropy-topsis-model.py` | AHP/entropy/TOPSIS experiment |
| `src/mcdm/pydecisions-mcdm.py` | pyDecision-based experiment |
| `src/visualization/mcdm-graphs.py` | Main comparison plot generator |
| `src/visualization/line-graph.py` | Additional plotting script |
| `src/geo/` | Geocoding and district/sub-district utilities |
| `gee-data-scripts/` | Google Earth Engine extraction scripts |
| `src/models/XGBoost.py` | XGBoost helper for missing `LST` values |

## Notes And Limitations

- Some Python files use hyphens in filenames, such as `dea-ahp-topsis.py`. These work as scripts but cannot be imported with normal Python import syntax.
- Several model files are script-style and execute immediately when run.
- The pipeline orchestrates the current scripts instead of refactoring the full codebase into a package.
- `data/First-sample.csv`, `data/all-method-score.csv`, and some generated CSVs are working copies created for compatibility with existing scripts.
- DEA optimization uses PuLP's bundled CBC solver, so model execution can print verbose solver output.
- OpenCage scripts require an API key before geocoding workflows can run.
- `src/models/XGBoost.py` currently contains a notebook-style input path and should be cleaned before production use.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Missing dependency | Run `source .venv/bin/activate` and `pip install -r requirements.txt` |
| Matplotlib cache warning | The pipeline sets `MPLCONFIGDIR` to `.cache/matplotlib` automatically |
| Missing model input | Verify `data/preprocessed/First-sample.csv` exists |
| Missing graph input | Verify `results/tables/all-method-score.csv` exists |
| Very noisy DEA output | Expected from PuLP/CBC solver logs in the current scripts |

## Future Improvements

Potential next steps:

- Refactor model scripts into reusable functions.
- Add command-line flags for choosing TOPSIS, MARCOS, VIKOR, or WASPAS.
- Remove duplicate working-copy outputs from `data/`.
- Add schema validation for model inputs and ranking outputs.
- Add tests for the pipeline and generated artifacts.
- Extend the framework toward Hybrid-ML + MCDM, including neural-network-based scoring, learned criteria weights, or ensemble ranking.

