Australian Tax Visualizer

## Dependencies

The only requirement is [uv](https://docs.astral.sh/uv/). All Python scripts use PEP 723 inline script metadata to automatically handle their dependencies when run with uv.

## Usage

All Python scripts can be run directly:

```bash
./create_plotly_chart.py
./create_inflation_redistributed_data.py  
./verify_redistribution.py
```

Or with uv explicitly:

```bash
uv run create_plotly_chart.py
uv run create_inflation_redistributed_data.py
uv run verify_redistribution.py
```

![Share](static/tax_cut_share.png)
