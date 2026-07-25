# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Interactive visualization of Australian individual taxpayer statistics from 2010-2024. A static website built with vanilla HTML/CSS/JavaScript using Plotly.js for charting. Data is preprocessed with Python and embedded directly in the generated `script.js`.

## Build Commands

```bash
# Extract the ATO workbook into the pipeline's CSVs
./extract_ato_source_data.py

# Generate the visualization (creates public/index.html and public/script.js)
./create_plotly_chart.py

# Or explicitly with uv
uv run create_plotly_chart.py

# Create inflation-redistributed dataset
./create_inflation_redistributed_data.py

# Verify redistribution calculations
./verify_redistribution.py
```

All Python scripts use PEP 723 inline script metadata—dependencies are handled automatically by uv.

## Architecture

### Data Pipeline

1. **Workbook**: `data/ts24individual03sextaxablestatusagerangetaxableincomerange.xlsx` — ATO Taxation Statistics 2023-24, Individuals Table 3. Sheet `Table 3B` is the multi-year sheet (2010-11 onwards); `Table 3A` is the latest year only and is unused.
2. **Raw CSV**: `data/ato_individual_tax_stats_by_demographics_2010_2024.csv` — all 52 workbook columns, sort prefixes rewritten
3. **Processed CSV**: `ato_2010-2024.csv` — normalized taxpayer data by income bracket, sex, age, taxable status
4. **Inflation-Adjusted**: `ato_2010-2024_inflation_redistributed.csv` — same data redistributed to 2023-24 equivalent brackets
5. **Output**: `public/index.html` and `public/script.js` — both written by `create_plotly_chart.py`, with data embedded as JSON

### Key Files

- `extract_ato_source_data.py` — Reads the ATO workbook and writes the raw, aggregate and normalized CSVs. Verified to reproduce the previous release's committed CSVs byte-for-byte from the `ts23` workbook.

- `create_plotly_chart.py` (1851 lines) — Main generator. Writes **both** `public/index.html` and `public/script.js`. Reads CSVs and produces complete `script.js` with:
  - Embedded data as JavaScript arrays
  - Chart rendering logic
  - UI state management
  - Tax bracket visualization
  - URL parameter sync

- `create_inflation_redistributed_data.py` — Applies CPI inflation factors to redistribute historical incomes into modern brackets

- `tax_rates/*.json` — Tax bracket definitions for each financial year (1990-91 through 2025-26)

- `inflation_factors_fy_correct.csv` — RBA inflation factors relative to 2023-24, scraped by `get_inflation_fy_correct.sh`

### Frontend Structure

- `public/index.html` — Generated file (do not edit directly); the template lives in `create_plotly_chart.py`
- `public/styles.css` — CSS variables for light/dark themes, responsive layout
- `public/script.js` — Generated file (do not edit directly)
- `public/plotly-3.0.1.min.js` — Vendored Plotly library

## Data Schema

CSV columns: `income_year`, `normalized_income_range`, `income_range_display`, `sex`, `taxable_status`, `age_range_display`, `individuals_count`, `total_income_amount`, `net_tax_amount`

Income ranges are ordered from "$6,000 or less" to "$1,000,001 or more" (15 brackets).

The ATO's own income ranges are finer (~28 per year) and their cut-points move with tax reform. `extract_ato_source_data.py` collapses each ATO range into the chart bracket holding its **upper** bound — this is what keeps shifting cut-points aligned (e.g. `$180,001 to $250,000` belongs with `$200,001 to $250,000`). Ranges that straddle a boundary (`$18,201 to $25,000`, `$37,001 to $41,000`) land wholly in the upper bracket, and the residual `$250,001 or more` bucket (14-52 people a year) joins `$250,001 to $500,000`.

## Development Notes

- The site is fully static—no build system, bundler, or dev server required
- Open `public/index.html` directly in a browser to test
- Changes to data or chart logic require re-running `create_plotly_chart.py`
- Theme switching (light/dark/system) is handled via CSS variables and body class

## Data Pipeline Internals

### Inflation Redistribution (`create_inflation_redistributed_data.py`)

Redistributes historical income data into 2023-24 equivalent brackets using CPI inflation factors.

**Algorithm**:
1. For each historical year, multiply income bracket bounds by inflation factor
2. Use Beta(2, 5) distribution to model right-skewed income distribution within each bracket
3. Calculate overlap between inflated source brackets and modern target brackets
4. Allocate individuals/income/tax proportionally based on overlap

**Key assumptions**:
- Beta(2, 5) parameters assume more people cluster toward lower end of each bracket (right-skewed). Actual within-bracket distribution is unknown.
- Upper bound for "$1,000,001 or more" bracket set to $2,000,000 for redistribution calculations. High earners above this effective ceiling are treated uniformly.
- Individual counts are rounded per-bracket; cumulative rounding error is ~0.05% per year (verified acceptable by `verify_redistribution.py`).

**Inflation factors** (loaded from `inflation_factors_fy_correct.csv`, base 2023-24):
| Year | Factor | Year | Factor |
|------|--------|------|--------|
| 2010-11 | 1.40 | 2017-18 | 1.22 |
| 2011-12 | 1.37 | 2018-19 | 1.20 |
| 2012-13 | 1.34 | 2019-20 | 1.18 |
| 2013-14 | 1.30 | 2020-21 | 1.17 |
| 2014-15 | 1.28 | 2021-22 | 1.12 |
| 2015-16 | 1.26 | 2022-23 | 1.04 |
| 2016-17 | 1.24 | 2023-24 | 1.00 |

### Chart Generation (`create_plotly_chart.py`)

**Data processing**:
1. Reads both nominal and redistributed CSVs
2. Groups by income bracket + demographics, sums numeric fields
3. Pre-calculates Y-axis maximums for all mode combinations (stacked/grouped, nominal/redistributed, absolute/percentage)
4. Embeds data as JSON directly into `script.js`

**Tax brackets**: Hardcoded in JavaScript output (the `taxBrackets` object, ~line 1385), not loaded from `tax_rates/*.json` files. Historical rates verified accurate including:
- 2012-13: Tax-free threshold raised to $18,200
- 2014-15 to 2016-17: 2% Budget Repair Levy (47% top rate)
- 2020-21: Tax cuts (32.5% extended to $120k)
- 2024-25: Stage 3 cuts (16% from $18,200, 30% from $45k)

**Income range ordering**: Hardcoded `income_range_order` list in `main()` must match CSV values exactly or chart sorting breaks. It duplicates `CHART_BRACKETS` in `extract_ato_source_data.py`; keep the two in step.

### Known Limitations

1. **Tax brackets manual** — `tax_rates/*.json` files exist but aren't used by chart generator; tax brackets are hardcoded in `create_plotly_chart.py`
2. **High-income approximation** — "$1,000,001 or more" bracket uses $2M ceiling for redistribution math
3. **Within-bracket distribution** — Beta(2,5) is a reasonable but unvalidated assumption
4. **Unused artifacts** — `data/chart_data.json`, `data/tax_data.json`, `ato_tax_data_normalized_for_chart.csv` and `tax_rates/*.json` are tracked but referenced by no code
5. **`fix_dash_consistency.py` is obsolete** — extraction now normalises year labels; the script is a no-op on generated data

## Updating to a New ATO Release

1. Find the new Individuals Table 3 resource via the CKAN API (the dataset page 403s non-browser clients):
   `curl -A '<browser UA>' 'https://data.gov.au/data/api/3/action/package_show?id=taxation-statistics-YYYY-YY'`
2. Download the workbook into `data/`
3. `./extract_ato_source_data.py --xlsx data/<new>.xlsx --end-year <YYYY>`
4. Rebase inflation: edit `BASE_START` in `get_inflation_fy_correct.sh`, then
   `./get_inflation_fy_correct.sh > inflation_factors_fy_correct.csv`
5. Update `BASE_YEAR`/`INPUT_CSV`/`OUTPUT_CSV` in `create_inflation_redistributed_data.py` and the two filenames in `verify_redistribution.py`
6. `./create_inflation_redistributed_data.py && ./verify_redistribution.py`
7. Update the CSV filenames and the year/base-year copy in `create_plotly_chart.py`, then `./create_plotly_chart.py`
8. Commit, then re-run `./create_plotly_chart.py` so the help modal's commit hash matches
