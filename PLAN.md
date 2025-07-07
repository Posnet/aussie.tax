# Interactive Australian Tax Data Visualization Plan

## Overview
Generate a self-contained HTML page visualizing Table 3B Australian taxation statistics (2010-11 to 2022-23).

## Chart Specifications

### Base Chart Type
- **Bar histogram** with stacked bars
- **X-axis**: Taxable income ranges (income brackets)
- **Y-axis**: Number of individuals

### Stacking and Coloring
- **Stack by**: Number of individuals in each tax bracket
- **Color options** (user selectable):
  - Taxable vs Non-taxable status
  - Male vs Female (gender)
  - Age brackets

### Interactive Features
- **Time scrubbing**: Gapminder-style year selector/slider
- **Animation**: Smooth transitions between years when scrubbing
- **Controls**: Dropdown/toggle for color scheme selection

## Data Source
- **Input**: Table 3B from `ts23individual03sextaxablestatusagerangetaxableincomerange.xlsx`
- **Time range**: 2010-11 to 2022-23 income years
- **Dimensions**: Sex, taxable status, age range, taxable income range

## Technical Requirements
- Self-contained HTML file (no external dependencies)
- Embedded JavaScript visualization library (D3.js or similar)
- Responsive design
- Smooth animations between time periods
- Interactive legend and controls