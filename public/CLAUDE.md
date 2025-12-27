# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Interactive visualization of Australian individual taxpayer statistics from 2010-2023. A static website built with vanilla HTML/CSS/JavaScript using Plotly.js for charting. Data is preprocessed with Python and embedded directly in the generated `script.js`.

## Build Commands

```bash
# Generate the visualization (creates public/script.js with embedded data)
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

1. **Source Data**: `data/ato_individual_tax_stats_by_demographics_2010_2023.csv` — raw ATO data
2. **Processed CSV**: `ato_2010-2023.csv` — normalized taxpayer data by income bracket, sex, age, taxable status
3. **Inflation-Adjusted**: `ato_2010-2023_inflation_redistributed.csv` — same data redistributed to 2022-23 equivalent brackets
4. **Output**: `public/script.js` — contains all chart logic with data embedded as JSON

### Key Files

- `create_plotly_chart.py` (1838 lines) — Main generator. Reads CSVs, tax rates, and produces complete `script.js` with:
  - Embedded data as JavaScript arrays
  - Chart rendering logic
  - UI state management
  - Tax bracket visualization
  - URL parameter sync

- `create_inflation_redistributed_data.py` — Applies CPI inflation factors to redistribute historical incomes into modern brackets

- `tax_rates/*.json` — Tax bracket definitions for each financial year (1990-91 through 2025-26)

- `inflation_factors_fy_correct.csv` — RBA inflation factors relative to 2022-23

### Frontend Structure

- `public/index.html` — Single page app shell with controls
- `public/styles.css` — CSS variables for light/dark themes, responsive layout
- `public/script.js` — Generated file (do not edit directly)
- `public/plotly-3.0.1.min.js` — Vendored Plotly library

## Data Schema

CSV columns: `income_year`, `normalized_income_range`, `income_range_display`, `sex`, `taxable_status`, `age_range_display`, `individuals_count`, `total_income_amount`, `net_tax_amount`

Income ranges are ordered from "$6,000 or less" to "$1,000,001 or more" (15 brackets).

## Development Notes

- The site is fully static—no build system, bundler, or dev server required
- Open `public/index.html` directly in a browser to test
- Changes to data or chart logic require re-running `create_plotly_chart.py`
- Theme switching (light/dark/system) is handled via CSS variables and body class

## Data Pipeline Internals

### Inflation Redistribution (`create_inflation_redistributed_data.py`)

Redistributes historical income data into 2022-23 equivalent brackets using CPI inflation factors.

**Algorithm**:
1. For each historical year, multiply income bracket bounds by inflation factor
2. Use Beta(2, 5) distribution to model right-skewed income distribution within each bracket
3. Calculate overlap between inflated source brackets and modern target brackets
4. Allocate individuals/income/tax proportionally based on overlap

**Key assumptions**:
- Beta(2, 5) parameters assume more people cluster toward lower end of each bracket (right-skewed). Actual within-bracket distribution is unknown.
- Upper bound for "$1,000,001 or more" bracket set to $2,000,000 for redistribution calculations. High earners above this effective ceiling are treated uniformly.
- Individual counts are rounded per-bracket; cumulative rounding error is ~0.05% per year (verified acceptable by `verify_redistribution.py`).

**Inflation factors** (loaded from `inflation_factors_fy_correct.csv`):
| Year | Factor | Year | Factor |
|------|--------|------|--------|
| 2010-11 | 1.34 | 2017-18 | 1.17 |
| 2011-12 | 1.31 | 2018-19 | 1.15 |
| 2012-13 | 1.28 | 2019-20 | 1.14 |
| 2013-14 | 1.25 | 2020-21 | 1.12 |
| 2014-15 | 1.23 | 2021-22 | 1.07 |
| 2015-16 | 1.21 | 2022-23 | 1.00 |
| 2016-17 | 1.19 | | |

### Chart Generation (`create_plotly_chart.py`)

**Data processing**:
1. Reads both nominal and redistributed CSVs
2. Groups by income bracket + demographics, sums numeric fields
3. Pre-calculates Y-axis maximums for all mode combinations (stacked/grouped, nominal/redistributed, absolute/percentage)
4. Embeds data as JSON directly into `script.js`

**Tax brackets**: Hardcoded in JavaScript output (lines 1365-1477), not loaded from `tax_rates/*.json` files. Historical rates verified accurate including:
- 2012-13: Tax-free threshold raised to $18,200
- 2014-15 to 2016-17: 2% Budget Repair Levy (47% top rate)
- 2020-21: Tax cuts (32.5% extended to $120k)
- 2024-25: Stage 3 cuts (16% from $18,200, 30% from $45k)

**Income range ordering**: Hardcoded list at line 45-61 must match CSV values exactly or chart sorting breaks.

### Known Limitations

1. **Tax brackets manual** — `tax_rates/*.json` files exist but aren't used by chart generator; tax brackets are hardcoded in `create_plotly_chart.py`
2. **High-income approximation** — "$1,000,001 or more" bracket uses $2M ceiling for redistribution math
3. **Within-bracket distribution** — Beta(2,5) is a reasonable but unvalidated assumption
