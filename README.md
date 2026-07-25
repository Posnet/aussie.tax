Australian Tax Visualizer

## Dependencies

The only requirement is [uv](https://docs.astral.sh/uv/). All Python scripts use PEP 723 inline script metadata to automatically handle their dependencies when run with uv.

## Usage

All Python scripts can be run directly, in pipeline order:

```bash
./extract_ato_source_data.py          # ATO workbook -> CSVs
./create_inflation_redistributed_data.py
./verify_redistribution.py
./create_plotly_chart.py              # -> public/index.html, public/script.js
```

Or with uv explicitly:

```bash
uv run extract_ato_source_data.py
uv run create_inflation_redistributed_data.py
uv run verify_redistribution.py
uv run create_plotly_chart.py
```

Current data: ATO Taxation Statistics 2023-24, Individuals Table 3 (financial
years 2010-11 through 2023-24). See `CLAUDE.md` for the pipeline details
and the steps to move to a newer release.

![Share](static/tax_cut_share.png)
