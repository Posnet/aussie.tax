#!/usr/bin/env python3
"""
Create an animated tax visualization using Plotly.
"""

import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px

def simplify_income_range(val):
    """Remove the sorting prefix for display."""
    if pd.isna(val):
        return val
    if '. ' in str(val):
        return str(val).split('. ', 1)[1]
    return str(val)

def simplify_age_range(val):
    """Remove the sorting prefix for display."""
    if pd.isna(val):
        return val
    if '. ' in str(val):
        return str(val).split('. ', 1)[1]
    return str(val)

def main():
    # Load the normalized data
    df = pd.read_csv('ato_tax_data_normalized_for_chart.csv')
    
    # Get unique values for controls
    years = sorted(df['income_year'].unique())
    
    # Define the proper order for income ranges
    income_range_order = [
        '$6,000 or less',
        '$6,001 to $10,000',
        '$10,001 to $20,000',
        '$20,001 to $30,000',
        '$30,001 to $40,000',
        '$40,001 to $50,000',
        '$50,001 to $60,000',
        '$60,001 to $80,000',
        '$80,001 to $100,000',
        '$100,001 to $150,000',
        '$150,001 to $200,000',
        '$200,001 to $250,000',
        '$250,001 to $500,000',
        '$500,001 to $1,000,000',
        '$1,000,001 or more'
    ]
    
    income_ranges = income_range_order
    income_ranges_display = income_ranges
    
    # Prepare data for Plotly
    plot_data = []
    
    # Process data for each year
    for year in years:
        year_df = df[df['income_year'] == year].copy()
        
        # Group by income range and aggregate
        grouped = year_df.groupby(['normalized_income_range', 'income_range_display', 'sex', 'taxable_status', 'age_range_display']).agg({
            'individuals_count': 'sum',
            'total_income_amount': 'sum',
            'net_tax_amount': 'sum'
        }).reset_index()
        
        # Add year column
        grouped['year'] = year
        plot_data.append(grouped)
    
    # Combine all data
    all_data = pd.concat(plot_data, ignore_index=True)
    
    # Create sort order for income ranges
    all_data['income_range_order'] = all_data['normalized_income_range'].apply(
        lambda x: income_range_order.index(x) if x in income_range_order else 999
    )
    all_data = all_data.sort_values(['year', 'income_range_order'])
    
    # Convert to JSON for embedding
    data_json = all_data.to_json(orient='records')
    
    # Create the HTML template with Plotly
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Australian Tax Distribution - Interactive Animation</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        :root {
            --bg-primary: #f8f8f8;
            --bg-secondary: #ffffff;
            --bg-tertiary: #f0f0f0;
            --text-primary: #333333;
            --text-secondary: #666666;
            --text-tertiary: #999999;
            --accent: #8b5cf6;
            --accent-hover: #7c3aed;
            --border: #e0e0e0;
            --grid: #f0f0f0;
            --error: #cc3333;
        }
        
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-primary: #1a1a1a;
                --bg-secondary: #242424;
                --bg-tertiary: #2a2a2a;
                --text-primary: #e0e0e0;
                --text-secondary: #a0a0a0;
                --text-tertiary: #707070;
                --accent: #a78bfa;
                --accent-hover: #c4b5fd;
                --border: #3a3a3a;
                --grid: #2a2a2a;
                --error: #ff6666;
            }
        }
        
        body.light-theme {
            --bg-primary: #f8f8f8;
            --bg-secondary: #ffffff;
            --bg-tertiary: #f0f0f0;
            --text-primary: #333333;
            --text-secondary: #666666;
            --text-tertiary: #999999;
            --accent: #8b5cf6;
            --accent-hover: #7c3aed;
            --border: #e0e0e0;
            --grid: #f0f0f0;
            --error: #cc3333;
        }
        
        body.dark-theme {
            --bg-primary: #1a1a1a;
            --bg-secondary: #242424;
            --bg-tertiary: #2a2a2a;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0a0;
            --text-tertiary: #707070;
            --accent: #a78bfa;
            --accent-hover: #c4b5fd;
            --border: #3a3a3a;
            --grid: #2a2a2a;
            --error: #ff6666;
        }
        
        body.dark-theme input[type="checkbox"]:checked + .toggle-switch {
            box-shadow: 0 0 8px rgba(167, 139, 250, 0.3);
        }
        
        body.dark-theme button:hover {
            box-shadow: 0 0 8px rgba(167, 139, 250, 0.3);
        }
        
        body {
            margin: 0;
            padding: 0;
            font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            overflow: hidden;
            font-size: 13px;
        }
        
        .container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding: 8px;
            box-sizing: border-box;
        }
        
        .header {
            background: var(--bg-secondary);
            padding: 8px 12px;
            border: 1px solid var(--border);
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 15px;
        }
        
        .header-left {
            flex: 1;
        }
        
        h1 {
            margin: 0 0 6px 0;
            color: var(--text-primary);
            font-size: 16px;
            font-weight: normal;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .controls {
            display: flex;
            gap: 12px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .control-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .control-group > label:first-child {
            font-size: 12px;
            font-weight: normal;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-right: 4px;
        }
        
        .data-source {
            margin-top: 6px;
            font-size: 11px;
            color: var(--text-tertiary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .data-source a {
            color: var(--accent);
            text-decoration: none;
        }
        
        .data-source a:hover {
            color: var(--accent-hover);
            text-decoration: underline;
        }
        
        select, button {
            padding: 4px 8px;
            border: 1px solid var(--border);
            background: var(--bg-tertiary);
            color: var(--text-primary);
            font-size: 12px;
            font-family: inherit;
            cursor: pointer;
            border-radius: 0;
        }
        
        select:focus, button:focus {
            outline: 1px solid var(--accent);
            outline-offset: -1px;
        }
        
        /* Custom toggle switch styles */
        input[type="checkbox"] {
            position: absolute;
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .control-group label {
            display: flex;
            align-items: center;
            cursor: pointer;
            user-select: none;
        }
        
        .control-group label span {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
            margin-left: 8px;
        }
        
        /* Toggle switch track */
        .toggle-switch {
            position: relative;
            display: inline-block;
            width: 32px;
            height: 18px;
            background-color: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* Toggle switch indicator */
        .toggle-switch::after {
            content: '';
            position: absolute;
            width: 14px;
            height: 14px;
            left: 2px;
            top: 2px;
            background-color: var(--text-tertiary);
            border-radius: 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        /* Checked state */
        input[type="checkbox"]:checked + .toggle-switch {
            background-color: var(--accent);
            border-color: var(--accent);
            box-shadow: 0 0 8px rgba(139, 92, 246, 0.25);
        }
        
        input[type="checkbox"]:checked + .toggle-switch::after {
            transform: translateX(14px);
            background-color: var(--bg-secondary);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
        }
        
        /* Hover state */
        .control-group label:hover .toggle-switch {
            background-color: var(--bg-tertiary);
            border-color: var(--accent);
        }
        
        input[type="checkbox"]:checked + .toggle-switch:hover {
            background-color: var(--accent-hover);
            border-color: var(--accent-hover);
        }
        
        /* Focus state */
        input[type="checkbox"]:focus-visible + .toggle-switch {
            outline: 2px solid var(--accent);
            outline-offset: 2px;
        }
        
        button {
            background: var(--bg-tertiary);
            color: var(--accent);
            border: 1px solid var(--border);
            transition: all 0.2s;
            font-weight: 500;
            letter-spacing: 0.5px;
        }
        
        button:hover {
            background: var(--accent);
            color: var(--bg-secondary);
            border-color: var(--accent);
            box-shadow: 0 0 8px rgba(139, 92, 246, 0.25);
        }
        
        @media (prefers-color-scheme: dark) {
            button {
                color: var(--accent);
            }
            
            input[type="checkbox"]:checked + .toggle-switch {
                box-shadow: 0 0 8px rgba(167, 139, 250, 0.3);
            }
            
            button:hover {
                box-shadow: 0 0 8px rgba(167, 139, 250, 0.3);
            }
        }
        
        button.playing {
            background: var(--accent);
            color: var(--bg-secondary);
            border-color: var(--accent);
        }
        
        button.playing:hover {
            background: var(--accent-hover);
            border-color: var(--accent-hover);
        }
        
        .theme-toggle {
            position: absolute;
            top: 8px;
            right: 8px;
            font-size: 11px;
            text-transform: uppercase;
            padding: 3px 6px;
            background: var(--accent);
            border: 1px solid var(--accent);
            color: var(--bg-secondary);
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .theme-toggle:hover {
            background: var(--accent-hover);
            border-color: var(--accent-hover);
        }
        
        .theme-toggle::after {
            content: attr(data-tooltip);
            position: absolute;
            top: 100%;
            right: 0;
            margin-top: 4px;
            padding: 4px 8px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            font-size: 10px;
            white-space: nowrap;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .theme-toggle:hover::after {
            opacity: 1;
        }
        
        #chart-container {
            flex: 1;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            position: relative;
            min-height: 0;
        }
        
        #chart {
            width: 100%;
            height: 100%;
        }
        
        .stats {
            background: var(--bg-tertiary);
            padding: 6px 10px;
            border: 1px solid var(--border);
            display: flex;
            gap: 15px;
        }
        
        .stat {
            display: flex;
            flex-direction: column;
            gap: 1px;
        }
        
        .stat-label {
            font-size: 11px;
            color: var(--text-tertiary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stat-value {
            font-size: 13px;
            font-weight: normal;
            color: var(--text-primary);
            font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace;
        }
        
        .stat-change {
            font-size: 11px;
            color: var(--text-tertiary);
            margin-left: 4px;
        }
        
        .stat-change.positive {
            color: #10b981;
        }
        
        .stat-change.negative {
            color: #ef4444;
        }
    </style>
</head>
<body>
    <button class="theme-toggle" id="themeToggle" data-tooltip="System theme">◐</button>
    <div class="container">
        <div class="header">
            <div class="header-left">
                <h1>AUS TAX DISTRIBUTION // INDIVIDUAL TAXPAYERS 2010-2023</h1>
                <div class="controls">
                    <div class="control-group">
                        <label for="colorBy">Color by:</label>
                        <select id="colorBy">
                            <option value="none">None</option>
                            <option value="age_range_display" selected>Age Group</option>
                            <option value="sex">Gender</option>
                            <option value="taxable_status">Taxable Status</option>
                        </select>
                    </div>
                    
                    <div class="control-group">
                        <label for="stackToggle">
                            <input type="checkbox" id="stackToggle" checked>
                            <div class="toggle-switch"></div>
                            <span>STACK</span>
                        </label>
                    </div>
                    
                    <div class="control-group">
                        <label for="percentageToggle">
                            <input type="checkbox" id="percentageToggle">
                            <div class="toggle-switch"></div>
                            <span>%</span>
                        </label>
                    </div>
                    
                    <div class="control-group">
                        <label for="logToggle">
                            <input type="checkbox" id="logToggle">
                            <div class="toggle-switch"></div>
                            <span>LOG</span>
                        </label>
                    </div>
                    
                    <div class="control-group">
                        <button id="playButton">▶ Play Animation</button>
                    </div>
                </div>
                <div class="data-source">
                    Data source: <a href="https://data.gov.au/data/dataset/taxation-statistics-2022-23/resource/a7f8226a-af03-431a-80f3-cdca85a9d63e" target="_blank" rel="noopener noreferrer">
                        Australian Taxation Office - Taxation Statistics 2022-23
                    </a>
                </div>
            </div>
            
            <div class="stats" id="stats">
                <div class="stat">
                    <span class="stat-label">Total Taxpayers:</span>
                    <span class="stat-value">
                        <span id="totalIndividuals">-</span>
                        <span class="stat-change" id="totalIndividualsChange"></span>
                    </span>
                </div>
                <div class="stat">
                    <span class="stat-label">Total Income:</span>
                    <span class="stat-value">
                        <span id="totalIncome">-</span>
                        <span class="stat-change" id="totalIncomeChange"></span>
                    </span>
                </div>
                <div class="stat">
                    <span class="stat-label">Total Tax:</span>
                    <span class="stat-value">
                        <span id="totalTax">-</span>
                        <span class="stat-change" id="totalTaxChange"></span>
                    </span>
                </div>
                <div class="stat">
                    <span class="stat-label">Effective Rate:</span>
                    <span class="stat-value">
                        <span id="effectiveRate">-</span>
                        <span class="stat-change" id="effectiveRateChange"></span>
                    </span>
                </div>
            </div>
        </div>
        
        <div id="chart-container">
            <div id="chart"></div>
        </div>
    </div>

    <script>
        // Embedded data
        const rawData = ''' + data_json + ''';
        
        // Parse and prepare data
        const data = rawData;
        const years = [...new Set(data.map(d => d.year))].sort();
        
        // Use the proper order for income ranges
        const incomeRanges = [
            '$6,000 or less',
            '$6,001 to $10,000',
            '$10,001 to $20,000',
            '$20,001 to $30,000',
            '$30,001 to $40,000',
            '$40,001 to $50,000',
            '$50,001 to $60,000',
            '$60,001 to $80,000',
            '$80,001 to $100,000',
            '$100,001 to $150,000',
            '$150,001 to $200,000',
            '$200,001 to $250,000',
            '$250,001 to $500,000',
            '$500,001 to $1,000,000',
            '$1,000,001 or more'
        ];
        const incomeRangesDisplay = incomeRanges;
        
        let currentFrame = 0;
        let isPlaying = false;
        let animationInterval = null;
        let currentTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        
        // Theme management
        function updateTheme(theme) {
            currentTheme = theme;
            document.body.classList.remove('light-theme', 'dark-theme');
            if (theme !== 'auto') {
                document.body.classList.add(theme + '-theme');
            }
            updateChart(currentFrame, document.getElementById('colorBy').value, 
                       document.getElementById('stackMode').value);
        }
        
        // Theme toggle button
        document.getElementById('themeToggle').addEventListener('click', function() {
            const themes = ['auto', 'light', 'dark'];
            const themeNames = ['System theme', 'Light theme', 'Dark theme'];
            const currentIndex = document.body.classList.contains('light-theme') ? 1 : 
                               document.body.classList.contains('dark-theme') ? 2 : 0;
            const nextIndex = (currentIndex + 1) % 3;
            const nextTheme = themes[nextIndex];
            
            this.textContent = nextTheme === 'auto' ? '◐' : nextTheme === 'light' ? '☀' : '☾';
            this.setAttribute('data-tooltip', themeNames[nextIndex]);
            updateTheme(nextTheme);
        });
        
        function updateChart(yearIndex, colorBy, stackMode) {
            const year = years[yearIndex];
            const yearData = data.filter(d => d.year === year);
            const valueMode = document.getElementById('percentageToggle').checked ? 'percentage' : 'absolute';
            const logScale = document.getElementById('logToggle').checked;
            const isStacked = document.getElementById('stackToggle').checked;
            stackMode = isStacked ? 'stack' : 'group';
            
            // Calculate total individuals for percentage mode
            const totalIndividuals = yearData.reduce((sum, d) => sum + d.individuals_count, 0);
            
            // Group data by income range and color category
            const grouped = {};
            yearData.forEach(d => {
                const key = d.normalized_income_range;
                if (!grouped[key]) {
                    grouped[key] = {};
                }
                const colorKey = d[colorBy];
                if (!grouped[key][colorKey]) {
                    grouped[key][colorKey] = 0;
                }
                grouped[key][colorKey] += d.individuals_count;
            });
            
            // Get unique color categories
            let colorCategories;
            
            if (colorBy === 'none') {
                colorCategories = ['All'];
            } else {
                colorCategories = [...new Set(data.map(d => d[colorBy]))].sort();
                
                // Special sorting for age ranges to ensure proper order
                if (colorBy === 'age_range_display') {
                    const ageOrder = [
                        'Under 18', '18 - 24', '25 - 29', '30 - 34', '35 - 39',
                        '40 - 44', '45 - 49', '50 - 54', '55 - 59', '60 - 64',
                        '65 - 69', '70 - 74', '75 and over'
                    ];
                    colorCategories = colorCategories.sort((a, b) => {
                        return ageOrder.indexOf(a) - ageOrder.indexOf(b);
                    });
                }
            }
            
            // Create traces for each color category
            const traces = colorCategories.map(category => {
                const yValues = incomeRanges.map(range => {
                    if (colorBy === 'none') {
                        // Sum all values for this income range
                        const value = Object.values(grouped[range] || {}).reduce((sum, val) => sum + val, 0);
                        return valueMode === 'percentage' ? (value / totalIndividuals) * 100 : value;
                    } else {
                        const value = grouped[range] && grouped[range][category] ? grouped[range][category] : 0;
                        return valueMode === 'percentage' ? (value / totalIndividuals) * 100 : value;
                    }
                });
                
                // Get color based on category
                let color;
                if (colorBy === 'none') {
                    color = '#8b5cf6';
                } else if (colorBy === 'age_range_display') {
                    const ageOrder = [
                        'Under 18', '18 - 24', '25 - 29', '30 - 34', '35 - 39',
                        '40 - 44', '45 - 49', '50 - 54', '55 - 59', '60 - 64',
                        '65 - 69', '70 - 74', '75 and over'
                    ];
                    const index = ageOrder.indexOf(category);
                    const colors = [
                        '#440154', '#482878', '#3e4989', '#31688e', '#26828e',
                        '#1f9e89', '#35b779', '#6ece58', '#b5de2b', '#fde725',
                        '#fee825', '#ffda25', '#ffc925'
                    ];
                    color = colors[index] || '#666666';
                } else if (colorBy === 'sex') {
                    color = category === 'Female' ? '#9b59b6' : '#f39c12';
                } else {
                    color = category === 'Taxable' ? '#8b5cf6' : '#e74c3c';
                }
                
                return {
                    name: category,
                    type: 'bar',
                    x: incomeRanges,
                    y: yValues,
                    hovertemplate: valueMode === 'percentage' 
                        ? '<b>%{x}</b><br>' + category + ': %{y:.2f}%<extra></extra>'
                        : '<b>%{x}</b><br>' + category + ': %{y:,.0f}<extra></extra>',
                    marker: { color: color }
                };
            });
            
            // Get theme colors - get computed styles to handle all theme cases
            const computedStyle = getComputedStyle(document.body);
            const colors = {
                bg: computedStyle.getPropertyValue('--bg-secondary').trim(),
                text: computedStyle.getPropertyValue('--text-primary').trim(),
                textSecondary: computedStyle.getPropertyValue('--text-secondary').trim(),
                grid: computedStyle.getPropertyValue('--grid').trim(),
                border: computedStyle.getPropertyValue('--border').trim(),
                accent: computedStyle.getPropertyValue('--accent').trim()
            };
            
            // Update layout
            const layout = {
                title: {
                    text: '',  // Remove title from top-left
                },
                barmode: stackMode,
                xaxis: {
                    title: {
                        text: 'Income Range (AUD)',
                        font: { size: 11, color: colors.textSecondary }
                    },
                    tickangle: -45,
                    automargin: true,
                    tickfont: { size: 11, color: colors.textSecondary },
                    gridcolor: colors.grid,
                    zerolinecolor: colors.border
                },
                yaxis: {
                    title: {
                        text: (valueMode === 'percentage' ? 'Percentage' : 'Individuals') + (logScale ? ' (log)' : ''),
                        font: { size: 11, color: colors.textSecondary }
                    },
                    type: logScale ? 'log' : 'linear',
                    tickformat: valueMode === 'percentage' ? '.1f' : ',.0f',
                    ticksuffix: valueMode === 'percentage' ? '%' : '',
                    tickfont: { size: 11, color: colors.textSecondary },
                    gridcolor: colors.grid,
                    zerolinecolor: colors.border
                },
                margin: { t: 25, r: 90, b: 160, l: 85 },
                showlegend: true,
                legend: {
                    orientation: 'v',
                    yanchor: 'middle',
                    y: 0.5,
                    xanchor: 'left',
                    x: 1.01,
                    font: { size: 11, color: colors.textSecondary },
                    bgcolor: 'rgba(0,0,0,0)',
                    bordercolor: colors.border,
                    borderwidth: 1
                },
                hovermode: 'closest',
                plot_bgcolor: colors.bg,
                paper_bgcolor: colors.bg,
                font: {
                    family: '"SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace',
                    color: colors.textSecondary
                },
                annotations: [{
                    text: year,
                    xref: 'paper',
                    yref: 'paper',
                    x: 1.01,
                    xanchor: 'left',
                    y: 0.85,
                    yanchor: 'bottom',
                    showarrow: false,
                    font: {
                        size: 16,
                        color: colors.text,
                        family: '"SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace'
                    }
                }]
            };
            
            // Always add slider with current position
            layout.sliders = [{
                active: yearIndex,
                currentvalue: {
                    visible: false
                },
                steps: years.map((yr, i) => ({
                    method: 'skip',
                    label: yr,
                    args: [i]
                })),
                pad: { t: 40, b: 10 },
                len: 0.9,
                x: 0.05,
                xanchor: 'left',
                y: -0.22,
                yanchor: 'top',
                bgcolor: colors.bg,
                bordercolor: colors.border,
                borderwidth: 1,
                font: { size: 11, color: colors.textSecondary },
                activebgcolor: colors.accent,
                tickcolor: colors.border
            }];
            
            // Create/update plot
            Plotly.react('chart', traces, layout, {
                responsive: true,
                displayModeBar: false
            });
            
            // Update stats
            updateStats(yearData, yearIndex);
        }
        
        let previousYearStats = null;
        
        function updateStats(yearData, yearIndex) {
            const totalIndividuals = yearData.reduce((sum, d) => sum + d.individuals_count, 0);
            const totalIncome = yearData.reduce((sum, d) => sum + d.total_income_amount, 0);
            const totalTax = yearData.reduce((sum, d) => sum + d.net_tax_amount, 0);
            const effectiveRate = totalIncome > 0 ? (totalTax / totalIncome) * 100 : 0;
            
            // Update current values
            document.getElementById('totalIndividuals').textContent = 
                totalIndividuals.toLocaleString();
            document.getElementById('totalIncome').textContent = 
                '$' + (totalIncome / 1e9).toFixed(1) + 'B';
            document.getElementById('totalTax').textContent = 
                '$' + (totalTax / 1e9).toFixed(1) + 'B';
            document.getElementById('effectiveRate').textContent = 
                effectiveRate.toFixed(1) + '%';
            
            // Calculate and show percentage changes if we have previous year data
            if (yearIndex > 0) {
                const prevYear = years[yearIndex - 1];
                const prevYearData = data.filter(d => d.year === prevYear);
                const prevTotalIndividuals = prevYearData.reduce((sum, d) => sum + d.individuals_count, 0);
                const prevTotalIncome = prevYearData.reduce((sum, d) => sum + d.total_income_amount, 0);
                const prevTotalTax = prevYearData.reduce((sum, d) => sum + d.net_tax_amount, 0);
                const prevEffectiveRate = prevTotalIncome > 0 ? (prevTotalTax / prevTotalIncome) * 100 : 0;
                
                // Calculate percentage changes
                const indivChange = ((totalIndividuals - prevTotalIndividuals) / prevTotalIndividuals) * 100;
                const incomeChange = ((totalIncome - prevTotalIncome) / prevTotalIncome) * 100;
                const taxChange = ((totalTax - prevTotalTax) / prevTotalTax) * 100;
                const rateChange = effectiveRate - prevEffectiveRate;
                
                // Update percentage displays
                updatePercentageDisplay('totalIndividualsChange', indivChange);
                updatePercentageDisplay('totalIncomeChange', incomeChange);
                updatePercentageDisplay('totalTaxChange', taxChange);
                updatePercentageDisplay('effectiveRateChange', rateChange, true);
            } else {
                // Clear percentage displays for first year
                document.getElementById('totalIndividualsChange').textContent = '';
                document.getElementById('totalIncomeChange').textContent = '';
                document.getElementById('totalTaxChange').textContent = '';
                document.getElementById('effectiveRateChange').textContent = '';
            }
        }
        
        function updatePercentageDisplay(elementId, change, isPoints = false) {
            const element = document.getElementById(elementId);
            if (Math.abs(change) < 0.01) {
                element.textContent = '(0.0%)';
                element.className = 'stat-change';
            } else {
                const sign = change > 0 ? '+' : '';
                const unit = isPoints ? 'pp' : '%';
                element.textContent = `(${sign}${change.toFixed(1)}${unit})`;
                element.className = change > 0 ? 'stat-change positive' : 'stat-change negative';
            }
        }
        
        // Event listeners
        document.getElementById('colorBy').addEventListener('change', function() {
            const stackMode = document.getElementById('stackToggle').checked ? 'stack' : 'group';
            updateChart(currentFrame, this.value, stackMode);
        });
        
        document.getElementById('stackToggle').addEventListener('change', function() {
            const stackMode = this.checked ? 'stack' : 'group';
            updateChart(currentFrame, document.getElementById('colorBy').value, stackMode);
        });
        
        document.getElementById('percentageToggle').addEventListener('change', function() {
            const stackMode = document.getElementById('stackToggle').checked ? 'stack' : 'group';
            updateChart(currentFrame, document.getElementById('colorBy').value, stackMode);
        });
        
        document.getElementById('logToggle').addEventListener('change', function() {
            const stackMode = document.getElementById('stackToggle').checked ? 'stack' : 'group';
            updateChart(currentFrame, document.getElementById('colorBy').value, stackMode);
        });
        
        document.getElementById('playButton').addEventListener('click', function() {
            if (isPlaying) {
                clearInterval(animationInterval);
                isPlaying = false;
                this.textContent = '▶ Play Animation';
                this.classList.remove('playing');
            } else {
                isPlaying = true;
                this.textContent = '⏸ Pause';
                this.classList.add('playing');
                
                // Get current settings before starting animation
                const currentColorBy = document.getElementById('colorBy').value;
                const currentStackMode = document.getElementById('stackToggle').checked ? 'stack' : 'group';
                
                animationInterval = setInterval(() => {
                    currentFrame = (currentFrame + 1) % years.length;
                    updateChart(currentFrame, currentColorBy, currentStackMode);
                    
                    if (currentFrame === years.length - 1) {
                        clearInterval(animationInterval);
                        isPlaying = false;
                        document.getElementById('playButton').textContent = '▶ Play Animation';
                        document.getElementById('playButton').classList.remove('playing');
                    }
                }, 1500);
            }
        });
        
        // Define color schemes
        const colorSchemes = {
            age_range_display: [
                '#440154', '#482878', '#3e4989', '#31688e', '#26828e',
                '#1f9e89', '#35b779', '#6ece58', '#b5de2b', '#fde725',
                '#fee825', '#ffda25', '#ffc925'
            ],
            sex: ['#9b59b6', '#f39c12'],
            taxable_status: ['#8b5cf6', '#e74c3c']
        };
        
        // Override Plotly's default color assignment
        Plotly.addTraces = (function(originalAddTraces) {
            return function(graphDiv, traces) {
                const colorBy = document.getElementById('colorBy').value;
                const colors = colorSchemes[colorBy];
                if (colors) {
                    traces.forEach((trace, i) => {
                        trace.marker = trace.marker || {};
                        trace.marker.color = colors[i % colors.length];
                    });
                }
                return originalAddTraces.apply(this, arguments);
            };
        })(Plotly.addTraces);
        
        // Initialize chart
        updateChart(0, 'age_range_display', 'stack');
        
        // Handle slider events
        document.getElementById('chart').on('plotly_sliderchange', function(eventdata) {
            if (!isPlaying) {  // Only respond to manual slider changes
                currentFrame = eventdata.slider.active;
                const stackMode = document.getElementById('stackToggle').checked ? 'stack' : 'group';
                updateChart(currentFrame, document.getElementById('colorBy').value, stackMode);
            }
        });
    </script>
</body>
</html>'''
    
    # Write the self-contained HTML file
    with open('ato_tax_plotly_chart.html', 'w') as f:
        f.write(html_content)
    
    print("✓ Created Plotly-based animated chart: ato_tax_plotly_chart.html")
    print("✓ Features:")
    print("  - Responsive design that fills the screen")
    print("  - Plotly stacked/grouped bar chart")
    print("  - Year slider with scrubbing capability")
    print("  - Color by Gender, Taxable Status, or Age Group")
    print("  - Play/pause animation")
    print("  - Real-time statistics display")

if __name__ == '__main__':
    main()