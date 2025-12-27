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
