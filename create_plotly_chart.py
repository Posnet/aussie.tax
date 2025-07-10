#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "pandas",
#     "plotly"
# ]
# ///
"""
Create an animated tax visualisation using Plotly.
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
    df = pd.read_csv('ato_2010-2023.csv')
    
    # Also load the inflation-redistributed data
    df_redistributed = pd.read_csv('ato_2010-2023_inflation_redistributed.csv')
    
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
    
    # Process redistributed data the same way
    plot_data_redistributed = []
    
    for year in years:
        year_df = df_redistributed[df_redistributed['income_year'] == year].copy()
        
        # Group by income range and aggregate
        grouped = year_df.groupby(['normalized_income_range', 'income_range_display', 'sex', 'taxable_status', 'age_range_display']).agg({
            'individuals_count': 'sum',
            'total_income_amount': 'sum',
            'net_tax_amount': 'sum'
        }).reset_index()
        
        # Add year column
        grouped['year'] = year
        plot_data_redistributed.append(grouped)
    
    # Combine all redistributed data
    all_data_redistributed = pd.concat(plot_data_redistributed, ignore_index=True)
    
    # Create sort order for income ranges
    all_data_redistributed['income_range_order'] = all_data_redistributed['normalized_income_range'].apply(
        lambda x: income_range_order.index(x) if x in income_range_order else 999
    )
    all_data_redistributed = all_data_redistributed.sort_values(['year', 'income_range_order'])
    
    # Convert redistributed data to JSON
    data_redistributed_json = all_data_redistributed.to_json(orient='records')
    
    # Calculate global maximums for each colorBy option
    # For stacked mode - always sum across all demographics per income range
    stacked_max_individuals = all_data.groupby(['year', 'normalized_income_range'])['individuals_count'].sum().max()
    stacked_max_income = all_data.groupby(['year', 'normalized_income_range'])['total_income_amount'].sum().max()
    stacked_max_tax = all_data.groupby(['year', 'normalized_income_range'])['net_tax_amount'].sum().max()
    
    # Also calculate maximums for redistributed data
    stacked_max_individuals_redis = all_data_redistributed.groupby(['year', 'normalized_income_range'])['individuals_count'].sum().max()
    stacked_max_income_redis = all_data_redistributed.groupby(['year', 'normalized_income_range'])['total_income_amount'].sum().max()
    stacked_max_tax_redis = all_data_redistributed.groupby(['year', 'normalized_income_range'])['net_tax_amount'].sum().max()
    
    # Calculate cumulative maximums - these will be much larger
    cumulative_max = {}
    for col in ['individuals_count', 'total_income_amount', 'net_tax_amount']:
        # For each year, calculate cumulative sum across income brackets
        max_cumul = 0
        for year in years:
            year_data = all_data[all_data['year'] == year]
            # Sum all values for the year (this is what cumulative will approach)
            year_total = year_data[col].sum()
            max_cumul = max(max_cumul, year_total)
        cumulative_max[col] = max_cumul
    
    print(f"  Cumulative maximums - individuals: {cumulative_max['individuals_count']:,.0f}, income: ${cumulative_max['total_income_amount']:,.0f}, tax: ${cumulative_max['net_tax_amount']:,.0f}")
    
    # For grouped mode - need to calculate for each colorBy option
    grouped_max = {}
    
    # When colorBy is 'none' - sum all demographics per income bracket
    grouped_max['none'] = {
        'individuals_count': all_data.groupby(['year', 'normalized_income_range'])['individuals_count'].sum().max(),
        'total_income_amount': all_data.groupby(['year', 'normalized_income_range'])['total_income_amount'].sum().max(),
        'net_tax_amount': all_data.groupby(['year', 'normalized_income_range'])['net_tax_amount'].sum().max()
    }
    
    # When colorBy is 'age_range_display' - max within each age group per income bracket
    grouped_max['age_range_display'] = {
        'individuals_count': all_data.groupby(['year', 'normalized_income_range', 'age_range_display'])['individuals_count'].sum().max(),
        'total_income_amount': all_data.groupby(['year', 'normalized_income_range', 'age_range_display'])['total_income_amount'].sum().max(),
        'net_tax_amount': all_data.groupby(['year', 'normalized_income_range', 'age_range_display'])['net_tax_amount'].sum().max()
    }
    
    # When colorBy is 'sex' - max within each sex per income bracket
    grouped_max['sex'] = {
        'individuals_count': all_data.groupby(['year', 'normalized_income_range', 'sex'])['individuals_count'].sum().max(),
        'total_income_amount': all_data.groupby(['year', 'normalized_income_range', 'sex'])['total_income_amount'].sum().max(),
        'net_tax_amount': all_data.groupby(['year', 'normalized_income_range', 'sex'])['net_tax_amount'].sum().max()
    }
    
    # When colorBy is 'taxable_status' - max within each status per income bracket
    grouped_max['taxable_status'] = {
        'individuals_count': all_data.groupby(['year', 'normalized_income_range', 'taxable_status'])['individuals_count'].sum().max(),
        'total_income_amount': all_data.groupby(['year', 'normalized_income_range', 'taxable_status'])['total_income_amount'].sum().max(),
        'net_tax_amount': all_data.groupby(['year', 'normalized_income_range', 'taxable_status'])['net_tax_amount'].sum().max()
    }
    
    # Calculate grouped maximums for redistributed data
    grouped_max_redis = {}
    
    grouped_max_redis['none'] = {
        'individuals_count': all_data_redistributed.groupby(['year', 'normalized_income_range'])['individuals_count'].sum().max(),
        'total_income_amount': all_data_redistributed.groupby(['year', 'normalized_income_range'])['total_income_amount'].sum().max(),
        'net_tax_amount': all_data_redistributed.groupby(['year', 'normalized_income_range'])['net_tax_amount'].sum().max()
    }
    
    grouped_max_redis['age_range_display'] = {
        'individuals_count': all_data_redistributed.groupby(['year', 'normalized_income_range', 'age_range_display'])['individuals_count'].sum().max(),
        'total_income_amount': all_data_redistributed.groupby(['year', 'normalized_income_range', 'age_range_display'])['total_income_amount'].sum().max(),
        'net_tax_amount': all_data_redistributed.groupby(['year', 'normalized_income_range', 'age_range_display'])['net_tax_amount'].sum().max()
    }
    
    grouped_max_redis['sex'] = {
        'individuals_count': all_data_redistributed.groupby(['year', 'normalized_income_range', 'sex'])['individuals_count'].sum().max(),
        'total_income_amount': all_data_redistributed.groupby(['year', 'normalized_income_range', 'sex'])['total_income_amount'].sum().max(),
        'net_tax_amount': all_data_redistributed.groupby(['year', 'normalized_income_range', 'sex'])['net_tax_amount'].sum().max()
    }
    
    grouped_max_redis['taxable_status'] = {
        'individuals_count': all_data_redistributed.groupby(['year', 'normalized_income_range', 'taxable_status'])['individuals_count'].sum().max(),
        'total_income_amount': all_data_redistributed.groupby(['year', 'normalized_income_range', 'taxable_status'])['total_income_amount'].sum().max(),
        'net_tax_amount': all_data_redistributed.groupby(['year', 'normalized_income_range', 'taxable_status'])['net_tax_amount'].sum().max()
    }
    
    print(f"Debug maximums:")
    print(f"  Stacked - individuals: {stacked_max_individuals:,.0f}, income: ${stacked_max_income:,.0f}, tax: ${stacked_max_tax:,.0f}")
    for color_by in grouped_max:
        max_indiv = grouped_max[color_by]['individuals_count']
        max_income = grouped_max[color_by]['total_income_amount'] 
        max_tax = grouped_max[color_by]['net_tax_amount']
        print(f"  Grouped ({color_by}) - individuals: {max_indiv:,.0f}, income: ${max_income:,.0f}, tax: ${max_tax:,.0f}")
    
    # Pre-calculate tick values for all combinations
    def calculate_ticks(max_val, is_money=False, is_log=False):
        """Calculate tick values and labels for a given max value."""
        if is_log:
            # For log scale, use powers of 10
            if is_money:
                ticks = [1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10, 1e11, 1e12]
                labels = ['$1K', '$10K', '$100K', '$1M', '$10M', '$100M', '$1B', '$10B', '$100B', '$1T']
            else:
                ticks = [1, 10, 100, 1000, 10000, 100000, 1000000, 10000000]
                labels = ['1', '10', '100', '1K', '10K', '100K', '1M', '10M']
            # Filter to only include ticks up to max_val * 2
            valid_ticks = [(t, l) for t, l in zip(ticks, labels) if t <= max_val * 2]
            return [t[0] for t in valid_ticks], [t[1] for t in valid_ticks]
        else:
            # Linear scale
            if is_money:
                if max_val <= 10e9:
                    step = 2e9
                elif max_val <= 30e9:
                    step = 5e9
                elif max_val <= 100e9:
                    step = 10e9
                elif max_val <= 300e9:
                    step = 20e9
                else:
                    step = 50e9
                
                ticks = []
                labels = []
                for i in range(0, int(max_val * 1.2), int(step)):
                    ticks.append(i)
                    if i == 0:
                        labels.append('$0')
                    elif i < 1e9:
                        labels.append(f'${i/1e6:.0f}M')
                    else:
                        labels.append(f'${i/1e9:.0f}B')
            else:
                # For individuals
                if max_val <= 100e3:  # 100K
                    step = 20e3  # 20K steps
                elif max_val <= 500e3:  # 500K
                    step = 100e3  # 100K steps
                elif max_val <= 2e6:  # 2M
                    step = 500e3  # 500K steps
                elif max_val <= 5e6:
                    step = 1e6
                elif max_val <= 20e6:
                    step = 2e6
                elif max_val <= 50e6:
                    step = 5e6
                else:
                    step = 10e6
                
                ticks = []
                labels = []
                for i in range(0, int(max_val * 1.2), int(step)):
                    ticks.append(i)
                    if i == 0:
                        labels.append('0')
                    elif i < 1e6:
                        labels.append(f'{i/1e3:.0f}K')
                    else:
                        labels.append(f'{i/1e6:.0f}M')
            
            return ticks, labels
    
    # Calculate percentage ticks
    def calculate_percentage_ticks(max_pct, is_log=False):
        """Calculate percentage tick values and labels."""
        if is_log:
            ticks = [0.01, 0.1, 1, 10, 100]
            labels = ['0.01%', '0.1%', '1%', '10%', '100%']
            valid_ticks = [(t, l) for t, l in zip(ticks, labels) if t <= max_pct * 2]
            return [t[0] for t in valid_ticks], [t[1] for t in valid_ticks]
        else:
            # Better step logic for small percentages
            if max_pct <= 1:
                step = 0.2
            elif max_pct <= 3:
                step = 0.5
            elif max_pct <= 5:
                step = 1
            elif max_pct <= 10:
                step = 2
            elif max_pct <= 25:
                step = 5
            elif max_pct <= 50:
                step = 10
            else:
                step = 20
            
            ticks = []
            labels = []
            i = 0
            while i <= max_pct * 1.2:
                ticks.append(i)
                labels.append(f'{i:g}%')  # Use :g to avoid unnecessary decimals
                i += step
            
            return ticks, labels
    
    # Calculate percentage max values properly
    # For percentage mode, values are % of total year
    # Stacked: sum of percentages in each income bracket
    # Grouped: individual percentage values (same as stacked, just not summed visually)
    
    # Calculate actual percentage maximums from data
    stacked_pct_max = {}
    grouped_pct_max = {
        'none': {},
        'age_range_display': {},
        'sex': {},
        'taxable_status': {}
    }
    
    for col in ['individuals_count', 'total_income_amount', 'net_tax_amount']:
        max_stacked = 0
        
        # Initialize max for each colorBy option
        for color_by in grouped_pct_max:
            grouped_pct_max[color_by][col] = 0
        
        for year in years:
            year_data = all_data[all_data['year'] == year]
            year_total = year_data[col].sum()
            
            if year_total > 0:
                # For each income bracket, calculate sum of percentages
                for income_range in income_range_order:
                    bracket_data = year_data[year_data['normalized_income_range'] == income_range]
                    bracket_sum = bracket_data[col].sum()
                    bracket_pct = (bracket_sum / year_total) * 100
                    max_stacked = max(max_stacked, bracket_pct)
                    
                    # For 'none' - the whole bracket is one bar
                    grouped_pct_max['none'][col] = max(grouped_pct_max['none'][col], bracket_pct)
                    
                    # For other colorBy options - need to group by that demographic
                    for color_by in ['age_range_display', 'sex', 'taxable_status']:
                        color_groups = bracket_data.groupby(color_by)[col].sum()
                        for group_val in color_groups:
                            group_pct = (group_val / year_total) * 100
                            grouped_pct_max[color_by][col] = max(grouped_pct_max[color_by][col], group_pct)
        
        stacked_pct_max[col] = max_stacked
        print(f"  {col} - stacked max %: {max_stacked:.2f}%")
        print(f"    grouped max % by colorBy option:")
        for color_by in grouped_pct_max:
            print(f"      {color_by}: {grouped_pct_max[color_by][col]:.2f}%")
    
    # Pre-calculate Y-axis ranges for all combinations
    y_ranges = {}
    
    # Helper to calculate range with padding
    def calculate_range(max_val, is_log=False, is_pct=False):
        if is_log:
            if is_pct:
                return [0.01, float(max_val * 2)]  # 0.01% to 2x max for log percentage
            elif max_val < 1000:
                return [1, float(max_val * 10)]
            else:
                return [1000, float(max_val * 10)]  # $1K minimum for money, 1 for counts
        else:
            return [0, float(max_val * 1.1)]  # 10% padding for linear
    
    # For now, just use the "none" grouped max as a default
    grouped_max_individuals = grouped_max['none']['individuals_count']
    grouped_max_income = grouped_max['none']['total_income_amount']
    grouped_max_tax = grouped_max['none']['net_tax_amount']
    
    # Absolute values
    y_ranges['stack_individuals_abs'] = calculate_range(stacked_max_individuals)
    y_ranges['stack_individuals_log'] = calculate_range(stacked_max_individuals, is_log=True)
    y_ranges['stack_income_abs'] = calculate_range(stacked_max_income)
    y_ranges['stack_income_log'] = calculate_range(stacked_max_income, is_log=True)
    y_ranges['stack_tax_abs'] = calculate_range(stacked_max_tax)
    y_ranges['stack_tax_log'] = calculate_range(stacked_max_tax, is_log=True)
    
    y_ranges['group_individuals_abs'] = calculate_range(grouped_max_individuals)
    y_ranges['group_individuals_log'] = calculate_range(grouped_max_individuals, is_log=True)
    y_ranges['group_income_abs'] = calculate_range(grouped_max_income)
    y_ranges['group_income_log'] = calculate_range(grouped_max_income, is_log=True)
    y_ranges['group_tax_abs'] = calculate_range(grouped_max_tax)
    y_ranges['group_tax_log'] = calculate_range(grouped_max_tax, is_log=True)
    
    # Percentage values
    y_ranges['stack_individuals_pct'] = calculate_range(stacked_pct_max['individuals_count'], is_pct=True)
    y_ranges['stack_individuals_pct_log'] = calculate_range(stacked_pct_max['individuals_count'], is_log=True, is_pct=True)
    y_ranges['stack_income_pct'] = calculate_range(stacked_pct_max['total_income_amount'], is_pct=True)
    y_ranges['stack_income_pct_log'] = calculate_range(stacked_pct_max['total_income_amount'], is_log=True, is_pct=True)
    y_ranges['stack_tax_pct'] = calculate_range(stacked_pct_max['net_tax_amount'], is_pct=True)
    y_ranges['stack_tax_pct_log'] = calculate_range(stacked_pct_max['net_tax_amount'], is_log=True, is_pct=True)
    
    # Use 'none' as default for the old y_ranges (these aren't used in the new implementation)
    y_ranges['group_individuals_pct'] = calculate_range(grouped_pct_max['none']['individuals_count'], is_pct=True)
    y_ranges['group_individuals_pct_log'] = calculate_range(grouped_pct_max['none']['individuals_count'], is_log=True, is_pct=True)
    y_ranges['group_income_pct'] = calculate_range(grouped_pct_max['none']['total_income_amount'], is_pct=True)
    y_ranges['group_income_pct_log'] = calculate_range(grouped_pct_max['none']['total_income_amount'], is_log=True, is_pct=True)
    y_ranges['group_tax_pct'] = calculate_range(grouped_pct_max['none']['net_tax_amount'], is_pct=True)
    y_ranges['group_tax_pct_log'] = calculate_range(grouped_pct_max['none']['net_tax_amount'], is_log=True, is_pct=True)
    
    # Pre-calculate all tick combinations
    tick_configs = {}
    
    # Absolute values - stacked
    tick_configs['stack_individuals_abs'] = calculate_ticks(stacked_max_individuals, is_money=False, is_log=False)
    tick_configs['stack_individuals_log'] = calculate_ticks(stacked_max_individuals, is_money=False, is_log=True)
    tick_configs['stack_income_abs'] = calculate_ticks(stacked_max_income, is_money=True, is_log=False)
    tick_configs['stack_income_log'] = calculate_ticks(stacked_max_income, is_money=True, is_log=True)
    tick_configs['stack_tax_abs'] = calculate_ticks(stacked_max_tax, is_money=True, is_log=False)
    tick_configs['stack_tax_log'] = calculate_ticks(stacked_max_tax, is_money=True, is_log=True)
    
    # Absolute values - grouped
    tick_configs['group_individuals_abs'] = calculate_ticks(grouped_max_individuals, is_money=False, is_log=False)
    tick_configs['group_individuals_log'] = calculate_ticks(grouped_max_individuals, is_money=False, is_log=True)
    tick_configs['group_income_abs'] = calculate_ticks(grouped_max_income, is_money=True, is_log=False)
    tick_configs['group_income_log'] = calculate_ticks(grouped_max_income, is_money=True, is_log=True)
    tick_configs['group_tax_abs'] = calculate_ticks(grouped_max_tax, is_money=True, is_log=False)
    tick_configs['group_tax_log'] = calculate_ticks(grouped_max_tax, is_money=True, is_log=True)
    
    # Percentage values - using calculated maximums
    tick_configs['stack_individuals_pct'] = calculate_percentage_ticks(stacked_pct_max['individuals_count'], is_log=False)
    tick_configs['stack_individuals_pct_log'] = calculate_percentage_ticks(stacked_pct_max['individuals_count'], is_log=True)
    tick_configs['stack_income_pct'] = calculate_percentage_ticks(stacked_pct_max['total_income_amount'], is_log=False)
    tick_configs['stack_income_pct_log'] = calculate_percentage_ticks(stacked_pct_max['total_income_amount'], is_log=True)
    tick_configs['stack_tax_pct'] = calculate_percentage_ticks(stacked_pct_max['net_tax_amount'], is_log=False)
    tick_configs['stack_tax_pct_log'] = calculate_percentage_ticks(stacked_pct_max['net_tax_amount'], is_log=True)
    
    tick_configs['group_individuals_pct'] = calculate_percentage_ticks(grouped_pct_max['none']['individuals_count'], is_log=False)
    tick_configs['group_individuals_pct_log'] = calculate_percentage_ticks(grouped_pct_max['none']['individuals_count'], is_log=True)
    tick_configs['group_income_pct'] = calculate_percentage_ticks(grouped_pct_max['none']['total_income_amount'], is_log=False)
    tick_configs['group_income_pct_log'] = calculate_percentage_ticks(grouped_pct_max['none']['total_income_amount'], is_log=True)
    tick_configs['group_tax_pct'] = calculate_percentage_ticks(grouped_pct_max['none']['net_tax_amount'], is_log=False)
    tick_configs['group_tax_pct_log'] = calculate_percentage_ticks(grouped_pct_max['none']['net_tax_amount'], is_log=True)
    
    # Convert to JSON for embedding
    tick_configs_json = json.dumps(tick_configs)
    y_ranges_json = json.dumps(y_ranges)
    
    # Debug output
    print("\nDebug - Y-axis ranges:")
    for key in sorted(y_ranges.keys()):
        print(f"  {key}: {y_ranges[key]}")
    
    print("\nDebug - Tick configs (first few ticks):")
    for key in sorted(tick_configs.keys()):
        vals, labels = tick_configs[key]
        if len(vals) > 0:
            print(f"  {key}: vals={vals[:3]}..., labels={labels[:3]}...")
        else:
            print(f"  {key}: EMPTY")
    
    # Create the HTML template with Plotly
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aussie Tax</title>
    <meta name="description" content="Interactive visualisation of Australian individual taxpayer statistics from 2010-2023. Explore income distribution, tax contributions, and demographic breakdowns across different income brackets.">
    <meta name="author" content="Posnet">
    <meta name="contact" content="aussie-tax@denialof.services">
    <meta name="theme-color" content="#02335c">

    <!-- Open Graph meta tags for better social media sharing -->
    <meta property="og:title" content="Aussie Tax">
    <meta property="og:description" content="Interactive visualisation of Australian individual taxpayer statistics from 2010-2023. Explore income distribution, tax contributions, and demographic breakdowns across different income brackets.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://aussie.tax">
    <meta property="og:image" content="https://aussie.tax/tax_cut_share.png">

    <!-- Twitter Card meta tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Aussie Tax">
    <meta name="twitter:description" content="Interactive visualisation of Australian individual taxpayer statistics from 2010-2023. Explore income distribution, tax contributions, and demographic breakdowns across different income brackets.">
    <meta name="twitter:image" content="https://aussie.tax/tax_cut_share.png">

    <!-- Canonical link to avoid duplicate content issues -->
    <link rel="canonical" href="https://aussie.tax">

    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-D1RYCL13D9"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-D1RYCL13D9');
    </script>

    <!-- Schema.org structured data for rich snippets -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": "Aussie Tax",
      "description": "Interactive visualisation of Australian individual taxpayer statistics from 2010-2023. Explore income distribution, tax contributions, and demographic breakdowns across different income brackets.",
      "author": {
        "@type": "Person",
        "name": "Posnet",
        "email": "aussie-tax@denialof.services"
      },
      "url": "https://aussie.tax",
      "image": "https://aussie.tax/tax_cut_share.png"
    }
    </script>

    <!-- Favicons and manifest -->
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="manifest" href="/site.webmanifest">

    <!-- Additional SEO best practices -->
    <meta name="robots" content="index, follow">
    <link rel="alternate" href="https://aussie.tax" hreflang="en">
    <link rel="sitemap" type="application/xml" title="Sitemap" href="https://aussie.tax/sitemap.xml">

    <!-- Stylesheets and scripts -->
    <link rel="stylesheet" href="/styles.css">
    <script src="plotly-3.0.1.min.js" charset="utf-8" defer></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <button class="theme-toggle" id="themeToggle" data-tooltip="System theme">◐</button>
            <div class="controls-section">
                <h1>AUSSIE TAX // INDIVIDUAL TAXPAYERS 2010-2023</h1>
                <div class="controls">
                    <div class="selectors-group">
                        <div class="control-group">
                            <label for="colorBy">Colour by:</label>
                            <select id="colorBy">
                                <option value="none">None</option>
                                <option value="age_range_display" selected>Age Group</option>
                                <option value="sex">Gender</option>
                                <option value="taxable_status">Taxable Status</option>
                            </select>
                        </div>
                        
                        <div class="control-group">
                            <label for="totalBy">Total by:</label>
                            <select id="totalBy">
                                <option value="individuals_count">Individuals</option>
                                <option value="total_income_amount">Total Income</option>
                                <option value="net_tax_amount" selected>Tax Paid</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="toggles-group">
                        <div class="toggles-row">
                            <div class="control-group">
                                <label for="stackToggle" data-tooltip="Stack/Group bars">
                                    <input type="checkbox" id="stackToggle" checked>
                                    <div class="toggle-switch"></div>
                                    <span id="stackIcon" class="toggle-icon">≡</span>
                                </label>
                            </div>
                            
                            <div class="control-group">
                                <label for="percentageToggle" data-tooltip="Show as percentage">
                                    <input type="checkbox" id="percentageToggle" checked>
                                    <div class="toggle-switch"></div>
                                    <span class="toggle-icon">％</span>
                                </label>
                            </div>
                            
                            <div class="control-group">
                                <label for="cumulativeToggle" data-tooltip="Cumulative view">
                                    <input type="checkbox" id="cumulativeToggle" checked>
                                    <div class="toggle-switch"></div>
                                    <span class="toggle-icon">∑</span>
                                </label>
                            </div>
                            
                            <div class="control-group">
                                <label for="logToggle" data-tooltip="Logarithmic scale">
                                    <input type="checkbox" id="logToggle">
                                    <div class="toggle-switch"></div>
                                    <span class="toggle-icon">L<sub>10</sub></span>
                                </label>
                            </div>
                            
                            <div class="control-group">
                                <label for="inflationToggle" data-tooltip="Show equivalent earners (infl. 2022-23 $)">
                                    <input type="checkbox" id="inflationToggle">
                                    <div class="toggle-switch"></div>
                                    <span class="toggle-icon">$<sub>23</sub></span>
                                </label>
                            </div>
                        </div>
                        
                        <div class="control-group play-button-group">
                            <button id="prevYear" class="nav-button mobile-only">◀◀</button>
                            <button id="playButton">▶ Play Animation</button>
                            <button id="nextYear" class="nav-button mobile-only">▶▶</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="stats-wrapper">
                <div class="stats" id="stats">
                    <div class="stats-row">
                        <div class="stat">
                            <span class="stat-label">Total Taxpayers:</span>
                            <span class="stat-value" id="totalIndividuals">-</span>
                            <span class="stat-change" id="totalIndividualsChange">(-%)</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Total Income:</span>
                            <span class="stat-value" id="totalIncome">-</span>
                            <span class="stat-change" id="totalIncomeChange">(-%)</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Total Tax:</span>
                            <span class="stat-value" id="totalTax">-</span>
                            <span class="stat-change" id="totalTaxChange">(-%)</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Effective Rate:</span>
                            <span class="stat-value" id="effectiveRate">-</span>
                            <span class="stat-change" id="effectiveRateChange">(-pp)</span>
                        </div>
                    </div>
                    <div class="tax-reform-note" id="taxReformNote">
                        <span class="note-label">FYI:</span>
                        <span class="note-text" id="taxReformText">-</span>
                    </div>
                </div>
            </div>
            
            <div class="tax-brackets" id="taxBrackets">
                <div class="tax-brackets-header">TAX BRACKETS</div>
                <div class="tax-brackets-viz" id="taxBracketsViz"></div>
            </div>
        </div>
        <button class="help-button mobile-only" id="helpButtonMobile">?</button>
        
        <div id="chart-container">
            <div id="chart"></div>
            <div class="help-text">← → arrow keys to navigate years</div>
        </div>
        
        <div class="data-source-bottom">
            Data source: <a href="https://data.gov.au/data/dataset/taxation-statistics-2022-23/resource/a7f8226a-af03-431a-80f3-cdca85a9d63e" target="_blank" rel="noopener noreferrer">
                Australian Taxation Office - Taxation Statistics 2022-23
            </a>
        </div>
    </div>
    
    <!-- Help Button -->
    <button class="help-button" id="helpButton">?</button>
    
    <!-- Help Modal -->
    <div id="helpModal" class="modal">
        <div class="modal-content">
            <span class="modal-close" id="modalClose">&times;</span>
            <h2>About This Visualisation</h2>
            
            <h3>Data Source</h3>
            <p>This visualisation uses data from the Australian Taxation Office (ATO) Taxation Statistics, specifically the Individual Sample Files from 2010-11 to 2022-23. The data represents all Australian individual taxpayers who lodged tax returns.</p>
            
            <h3>Key Metrics</h3>
            <ul>
                <li><strong>Individuals:</strong> Number of taxpayers in each income bracket</li>
                <li><strong>Total Income:</strong> Combined taxable income of all individuals</li>
                <li><strong>Tax Paid:</strong> Total net tax paid after offsets and deductions</li>
                <li><strong>Effective Rate:</strong> Percentage of income paid as tax (tax ÷ income)</li>
            </ul>
            
            <h3>Income Brackets</h3>
            <p>The ATO groups taxpayers into income ranges. The highest bracket "$1,000,001 or more" includes all very high earners, which can skew averages in that bracket.</p>
            
            <h3>Inflation Adjustment ($<sub>23</sub>)</h3>
            <p>When enabled, this feature shows "equivalent earners" - people who had the same purchasing power in historical years as someone earning that amount in 2022-23.</p>
            <p><strong>How it works:</strong></p>
            <ul>
                <li>Uses RBA inflation data to convert historical incomes to 2022-23 dollars</li>
                <li>Redistributes people into modern income brackets based on their inflation-adjusted income</li>
                <li>Example: Someone earning $50,000 in 2010-11 had the purchasing power of $67,000 in 2022-23</li>
            </ul>
            <p><strong>Important:</strong> This shows where people <em>would</em> be distributed if their purchasing power was translated to today's dollars, not actual income growth.</p>
            
            <h3>View Options</h3>
            <ul>
                <li><strong>Stack/Group (≡/⦀):</strong> Stack bars on top of each other or place side by side</li>
                <li><strong>Percentage (%):</strong> Show values as percentage of year total instead of absolute numbers</li>
                <li><strong>Cumulative (∑):</strong> Each bar includes all lower income brackets</li>
                <li><strong>Logarithmic (L<sub>10</sub>):</strong> Use log scale for better visibility of small values</li>
            </ul>
            
            <h3>Demographics</h3>
            <ul>
                <li><strong>Age Groups:</strong> Based on age at end of financial year</li>
                <li><strong>Gender:</strong> As recorded in tax return</li>
                <li><strong>Taxable Status:</strong> Whether net tax was payable after deductions/offsets</li>
            </ul>
            
            <h3>Known Limitations</h3>
            <ul>
                <li>Negative incomes (business losses) can affect low bracket totals</li>
                <li>Capital gains are included in taxable income</li>
                <li>Excludes people who didn't lodge tax returns</li>
                <li>Tax calculations include income tax, capital gains tax, Medicare levy and other levies</li>
                <li>Income brackets are based on taxable income, which includes net capital gains</li>
            </ul>
            
            <h3>Source Code</h3>
            <p><a href="https://github.com/Posen2101024/aussie.tax" target="_blank" rel="noopener noreferrer">github.com/Posen2101024/aussie.tax</a></p>
        </div>
    </div>
    
    <script src="script.js"></script>
</body>
</html>'''

    script_content = '''// Wait for Plotly to be loaded
if (typeof Plotly === 'undefined') {
    window.addEventListener('load', initChart);
} else {
    initChart();
}

function initChart() {
    // Embedded data
    const rawData = ''' + data_json + ''';
    const rawDataRedistributed = ''' + data_redistributed_json + ''';
    
    // Store both datasets
    const datasets = {
        nominal: rawData,
        redistributed: rawDataRedistributed
    };

    // Pre-calculated maximums for each combination
const maximums = {
    nominal: {
        stacked: {
            individuals_count: ''' + str(int(stacked_max_individuals)) + ''',
            total_income_amount: ''' + str(int(stacked_max_income)) + ''',
            net_tax_amount: ''' + str(int(stacked_max_tax)) + '''
        },
        grouped: ''' + json.dumps({k: {col: int(v[col]) for col in v} for k, v in grouped_max.items()}) + '''
    },
    redistributed: {
        stacked: {
            individuals_count: ''' + str(int(stacked_max_individuals_redis)) + ''',
            total_income_amount: ''' + str(int(stacked_max_income_redis)) + ''',
            net_tax_amount: ''' + str(int(stacked_max_tax_redis)) + '''
        },
        grouped: ''' + json.dumps({k: {col: int(v[col]) for col in v} for k, v in grouped_max_redis.items()}) + '''
    },
    cumulative: {
        individuals_count: ''' + str(int(cumulative_max['individuals_count'])) + ''',
        total_income_amount: ''' + str(int(cumulative_max['total_income_amount'])) + ''',
        net_tax_amount: ''' + str(int(cumulative_max['net_tax_amount'])) + '''
    }
};

// Pre-calculated percentage maximums
const percentageMaximums = {
    stacked: {
        individuals_count: ''' + str(stacked_pct_max['individuals_count']) + ''',
        total_income_amount: ''' + str(stacked_pct_max['total_income_amount']) + ''',
        net_tax_amount: ''' + str(stacked_pct_max['net_tax_amount']) + '''
    },
    grouped: ''' + json.dumps(grouped_pct_max) + '''
};

// Get current dataset based on inflation toggle
function getCurrentData() {
    const isInflationAdjusted = document.getElementById('inflationToggle') && 
                                document.getElementById('inflationToggle').checked;
    return isInflationAdjusted ? datasets.redistributed : datasets.nominal;
}

// Parse and prepare data
let data = getCurrentData();
const years = [...new Set(datasets.nominal.map(d => d.year))].sort();

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

// Mobile-friendly abbreviated labels
const incomeRangesMobile = [
    '≤$6K',
    '$6-10K',
    '$10-20K',
    '$20-30K',
    '$30-40K',
    '$40-50K',
    '$50-60K',
    '$60-80K',
    '$80-100K',
    '$100-150K',
    '$150-200K',
    '$200-250K',
    '$250-500K',
    '$500K-1M',
    '>$1M'
];

const incomeRangesDisplay = window.innerWidth <= 768 ? incomeRangesMobile : incomeRanges;

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
    // Update chart with current settings to apply new theme colors
    const stackMode = document.getElementById('stackToggle').checked ? 'stack' : 'group';
    updateChart(currentFrame, document.getElementById('colorBy').value, stackMode);
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
        
        // Helper functions for Y-axis formatting
        function getYAxisTitle(totalBy, valueMode, isCumulative, isInflationAdjusted) {
            let title = '';
            if (valueMode === 'percentage') {
                title = 'Percentage';
            } else {
                switch(totalBy) {
                    case 'individuals_count': title = 'Individuals'; break;
                    case 'total_income_amount': title = isInflationAdjusted ? 'Total Income (2022-23 $)' : 'Total Income (AUD)'; break;
                    case 'net_tax_amount': title = isInflationAdjusted ? 'Tax Paid (2022-23 $)' : 'Tax Paid (AUD)'; break;
                    default: title = 'Value';
                }
            }
            return isCumulative ? 'Cumulative ' + title : title;
        }
        
        function getTickFormat(totalBy, valueMode) {
            if (valueMode === 'percentage') return '.1f';
            if (totalBy === 'individuals_count') return ',.0f';
            return '$.3s'; // Better currency format (e.g., $1.23B)
        }
        
        function getHoverTemplate(totalBy, valueMode, category) {
            if (valueMode === 'percentage') {
                return '<b>%{x}</b><br>' + category + ': %{y:.2f}%<extra></extra>';
            }
            switch(totalBy) {
                case 'individuals_count':
                    return '<b>%{x}</b><br>' + category + ': %{y:,.0f}<extra></extra>';
                case 'total_income_amount':
                    return '<b>%{x}</b><br>' + category + ': $%{y:,.0f}<extra></extra>';
                case 'net_tax_amount':
                    return '<b>%{x}</b><br>' + category + ': $%{y:,.0f}<extra></extra>';
                default:
                    return '<b>%{x}</b><br>' + category + ': %{y:,.0f}<extra></extra>';
            }
        }
        
        
        function updateChart(yearIndex, colorBy, stackMode) {
            const year = years[yearIndex];
            
            // Update data based on inflation toggle
            data = getCurrentData();
            
            const yearData = data.filter(d => d.year === year);
            const valueMode = document.getElementById('percentageToggle').checked ? 'percentage' : 'absolute';
            const logScale = document.getElementById('logToggle').checked;
            const isCumulative = document.getElementById('cumulativeToggle').checked;
            const isStacked = document.getElementById('stackToggle').checked;
            const isInflationAdjusted = document.getElementById('inflationToggle').checked;
            stackMode = isStacked ? 'stack' : 'group';
            const totalBy = document.getElementById('totalBy').value;
            
            // Calculate total for percentage mode
            const totalValue = yearData.reduce((sum, d) => sum + d[totalBy], 0);
            
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
                grouped[key][colorKey] += d[totalBy];
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
                        return valueMode === 'percentage' ? (value / totalValue) * 100 : value;
                    } else {
                        const value = grouped[range] && grouped[range][category] ? grouped[range][category] : 0;
                        // Percentage is always calculated the same way - as % of total year
                        return valueMode === 'percentage' ? (value / totalValue) * 100 : value;
                    }
                });
                
                // Apply cumulative calculation if enabled
                if (isCumulative) {
                    let cumulativeSum = 0;
                    for (let i = 0; i < yValues.length; i++) {
                        cumulativeSum += yValues[i];
                        yValues[i] = cumulativeSum;
                    }
                }
                
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
                    x: window.innerWidth <= 768 ? incomeRangesMobile : incomeRanges,
                    y: yValues,
                    hovertemplate: getHoverTemplate(totalBy, valueMode, category),
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
                yaxis: (() => {
                    // Get the correct maximum for current settings
                    let maxVal;
                    const datasetKey = isInflationAdjusted ? 'redistributed' : 'nominal';
                    
                    if (isCumulative) {
                        // For cumulative, use the pre-calculated cumulative maximums
                        maxVal = maximums.cumulative[totalBy];
                    } else if (stackMode === 'stack') {
                        maxVal = maximums[datasetKey].stacked[totalBy];
                    } else {
                        maxVal = maximums[datasetKey].grouped[colorBy][totalBy];
                    }
                    
                    // For linear scale only, set a fixed range based on the maximum
                    // For log scale, let Plotly auto-scale
                    let yAxisConfig = {
                        title: {
                            text: getYAxisTitle(totalBy, valueMode, isCumulative, isInflationAdjusted) + (logScale ? ' (log)' : ''),
                            font: { size: 11, color: colors.textSecondary }
                        },
                        type: logScale ? 'log' : 'linear',
                        tickfont: { size: 11, color: colors.textSecondary },
                        gridcolor: colors.grid,
                        zerolinecolor: colors.border
                    };
                    
                    // Add prefix/suffix for money and percentage
                    if (valueMode === 'percentage') {
                        yAxisConfig.ticksuffix = '%';
                    } else if (totalBy !== 'individuals_count') {
                        yAxisConfig.tickprefix = '$';
                    }
                    
                    // Set range for both linear and log scale to keep consistent
                    if (logScale) {
                        // For log scale, set min/max range but let Plotly handle tickers
                        if (valueMode === 'percentage') {
                            // Use pre-calculated percentage maximums
                            let pctMax;
                            if (isCumulative) {
                                // For cumulative percentages, max should be exactly 100%
                                pctMax = 100;
                                yAxisConfig.range = [Math.log10(0.01), Math.log10(100)]; // Cap at 100%
                            } else {
                                pctMax = stackMode === 'stack' ? 
                                    percentageMaximums.stacked[totalBy] : 
                                    percentageMaximums.grouped[colorBy][totalBy];
                                yAxisConfig.range = [Math.log10(0.01), Math.log10(pctMax * 1.2)]; // log range with padding
                            }
                        } else {
                            const minVal = Math.max(1, maxVal * 0.001); // Avoid log(0)
                            yAxisConfig.range = [Math.log10(minVal), Math.log10(maxVal * 1.1)];
                        }
                    } else {
                        // Linear scale
                        if (valueMode === 'percentage') {
                            // Use pre-calculated percentage maximums
                            let pctMax;
                            if (isCumulative) {
                                // For cumulative percentages, max should be exactly 100%
                                pctMax = 100;
                                yAxisConfig.range = [0, 100]; // Cap at 100%
                            } else {
                                pctMax = stackMode === 'stack' ? 
                                    percentageMaximums.stacked[totalBy] : 
                                    percentageMaximums.grouped[colorBy][totalBy];
                                yAxisConfig.range = [0, pctMax * 1.2]; // 20% padding
                            }
                        } else {
                            yAxisConfig.range = [0, maxVal * 1.1];
                        }
                    }
                    
                    return yAxisConfig;
                })(),
                margin: window.innerWidth <= 768 ? 
                    { t: 20, r: 10, b: 80, l: 60 } : 
                    { t: 40, r: 150, b: 120, l: 70 },
                showlegend: window.innerWidth > 768,
                legend: {
                    orientation: 'v',
                    yanchor: 'top',
                    y: 0.75,
                    xanchor: 'left',
                    x: 1.01,
                    font: { size: 11, color: colors.textSecondary },
                    bgcolor: colors.bg,
                    bordercolor: colors.border,
                    borderwidth: 1,
                    traceorder: 'normal'
                },
                hovermode: 'closest',
                plot_bgcolor: colors.bg,
                paper_bgcolor: colors.bg,
                font: {
                    family: '"SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace',
                    color: colors.textSecondary
                },
                annotations: window.innerWidth > 768 ? [{
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
                }] : []
            };
            
            // Update tax reform note
            const taxReformNote = document.getElementById('taxReformNote');
            const taxReformText = document.getElementById('taxReformText');
            
            if (year === '2012–13') {
                taxReformNote.classList.remove('empty');
                taxReformText.textContent = 'Tax-free increased from $6,000 to $18,200';
            } else if (year === '2014–15' || year === '2015–16') {
                taxReformNote.classList.remove('empty');
                taxReformText.textContent = 'Repair Levy: 45% + 2% = 47% rate >$180k';
            } else if (year === '2016–17') {
                taxReformNote.classList.remove('empty');
                taxReformText.textContent = '32.5% to $87k; Repair Levy: 47% on >$180k';
            } else if (year === '2020–21') {
                taxReformNote.classList.remove('empty');
                taxReformText.textContent = 'Tax cuts: 32.5% to $120k, 37% to $180k';
            } else if (year === '2024–25' || year === '2025–26') {
                taxReformNote.classList.remove('empty');
                taxReformText.textContent = 'Stage 3 tax cuts';
            } else {
                taxReformNote.classList.add('empty');
                taxReformText.textContent = '-';
            }
            
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
                pad: { t: window.innerWidth <= 768 ? 10 : 40, b: 10 },
                len: 0.9,
                x: 0.05,
                xanchor: 'left',
                y: window.innerWidth <= 768 ? -0.15 : -0.22,
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
            
            // Update stats and tax brackets
            updateStats(yearData, yearIndex);
            updateTaxBrackets(year);
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
                // Show greyed out placeholders for first year
                document.getElementById('totalIndividualsChange').textContent = '(-%)'
                document.getElementById('totalIndividualsChange').className = 'stat-change';
                document.getElementById('totalIncomeChange').textContent = '(-%)'
                document.getElementById('totalIncomeChange').className = 'stat-change';
                document.getElementById('totalTaxChange').textContent = '(-%)'
                document.getElementById('totalTaxChange').className = 'stat-change';
                document.getElementById('effectiveRateChange').textContent = '(-pp)'
                document.getElementById('effectiveRateChange').className = 'stat-change';
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
            updateURLParams();
        });
        
        document.getElementById('totalBy').addEventListener('change', function() {
            const stackMode = document.getElementById('stackToggle').checked ? 'stack' : 'group';
            updateChart(currentFrame, document.getElementById('colorBy').value, stackMode);
            updateURLParams();
        });
        
        document.getElementById('stackToggle').addEventListener('change', function() {
            const stackMode = this.checked ? 'stack' : 'group';
            const stackIcon = document.getElementById('stackIcon');
            stackIcon.textContent = this.checked ? '≡' : '⦀';
            updateChart(currentFrame, document.getElementById('colorBy').value, stackMode);
            updateURLParams();
        });
        
        document.getElementById('percentageToggle').addEventListener('change', function() {
            const stackMode = document.getElementById('stackToggle').checked ? 'stack' : 'group';
            updateChart(currentFrame, document.getElementById('colorBy').value, stackMode);
            updateURLParams();
        });
        
        document.getElementById('logToggle').addEventListener('change', function() {
            const stackMode = document.getElementById('stackToggle').checked ? 'stack' : 'group';
            updateChart(currentFrame, document.getElementById('colorBy').value, stackMode);
            updateURLParams();
        });
        
        document.getElementById('cumulativeToggle').addEventListener('change', function() {
            const stackMode = document.getElementById('stackToggle').checked ? 'stack' : 'group';
            updateChart(currentFrame, document.getElementById('colorBy').value, stackMode);
            updateURLParams();
        });
        
        document.getElementById('inflationToggle').addEventListener('change', function() {
            const stackMode = document.getElementById('stackToggle').checked ? 'stack' : 'group';
            updateChart(currentFrame, document.getElementById('colorBy').value, stackMode);
            updateURLParams();
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
                    updateNavButtons();
                    updateURLParams();
                    
                    if (currentFrame === years.length - 1) {
                        clearInterval(animationInterval);
                        isPlaying = false;
                        document.getElementById('playButton').textContent = '▶ Play Animation';
                        document.getElementById('playButton').classList.remove('playing');
                    }
                }, 1500);
            }
        });
        
        // Tax bracket data for each year
        const taxBrackets = {
            '2010–11': [
                { threshold: 0, rate: 0, color: '#f4f0fe' },
                { threshold: 6000, rate: 15, color: '#c4b5fd' },
                { threshold: 37000, rate: 30, color: '#a78bfa' },
                { threshold: 80000, rate: 37, color: '#8b5cf6' },
                { threshold: 180000, rate: 45, color: '#7c3aed' }
            ],
            '2011–12': [
                { threshold: 0, rate: 0, color: '#f4f0fe' },
                { threshold: 6000, rate: 15, color: '#c4b5fd' },
                { threshold: 37000, rate: 30, color: '#a78bfa' },
                { threshold: 80000, rate: 37, color: '#8b5cf6' },
                { threshold: 180000, rate: 45, color: '#7c3aed' }
            ],
            '2012–13': [
                { threshold: 0, rate: 0, color: '#f4f0fe' },
                { threshold: 18200, rate: 19, color: '#c4b5fd' },
                { threshold: 37000, rate: 32.5, color: '#a78bfa' },
                { threshold: 80000, rate: 37, color: '#8b5cf6' },
                { threshold: 180000, rate: 45, color: '#7c3aed' }
            ],
            '2013–14': [
                { threshold: 0, rate: 0, color: '#f4f0fe' },
                { threshold: 18200, rate: 19, color: '#c4b5fd' },
                { threshold: 37000, rate: 32.5, color: '#a78bfa' },
                { threshold: 80000, rate: 37, color: '#8b5cf6' },
                { threshold: 180000, rate: 45, color: '#7c3aed' }
            ],
            '2014–15': [
                { threshold: 0, rate: 0, color: '#f4f0fe' },
                { threshold: 18200, rate: 19, color: '#c4b5fd' },
                { threshold: 37000, rate: 32.5, color: '#a78bfa' },
                { threshold: 80000, rate: 37, color: '#8b5cf6' },
                { threshold: 180000, rate: 47, color: '#6b21a8' }  // Includes 2% budget repair levy
            ],
            '2015–16': [
                { threshold: 0, rate: 0, color: '#f4f0fe' },
                { threshold: 18200, rate: 19, color: '#c4b5fd' },
                { threshold: 37000, rate: 32.5, color: '#a78bfa' },
                { threshold: 80000, rate: 37, color: '#8b5cf6' },
                { threshold: 180000, rate: 47, color: '#6b21a8' }  // Includes 2% budget repair levy
            ],
            '2016–17': [
                { threshold: 0, rate: 0, color: '#f4f0fe' },
                { threshold: 18200, rate: 19, color: '#c4b5fd' },
                { threshold: 37000, rate: 32.5, color: '#a78bfa' },
                { threshold: 87000, rate: 37, color: '#8b5cf6' },
                { threshold: 180000, rate: 47, color: '#6b21a8' }  // Includes 2% budget repair levy
            ],
            '2017–18': [
                { threshold: 0, rate: 0, color: '#f4f0fe' },
                { threshold: 18200, rate: 19, color: '#c4b5fd' },
                { threshold: 37000, rate: 32.5, color: '#a78bfa' },
                { threshold: 87000, rate: 37, color: '#8b5cf6' },
                { threshold: 180000, rate: 45, color: '#7c3aed' }
            ],
            '2018–19': [
                { threshold: 0, rate: 0, color: '#f4f0fe' },
                { threshold: 18200, rate: 19, color: '#c4b5fd' },
                { threshold: 37000, rate: 32.5, color: '#a78bfa' },
                { threshold: 90000, rate: 37, color: '#8b5cf6' },
                { threshold: 180000, rate: 45, color: '#7c3aed' }
            ],
            '2019–20': [
                { threshold: 0, rate: 0, color: '#f4f0fe' },
                { threshold: 18200, rate: 19, color: '#c4b5fd' },
                { threshold: 37000, rate: 32.5, color: '#a78bfa' },
                { threshold: 90000, rate: 37, color: '#8b5cf6' },
                { threshold: 180000, rate: 45, color: '#7c3aed' }
            ],
            '2020–21': [
                { threshold: 0, rate: 0, color: '#f4f0fe' },
                { threshold: 18200, rate: 19, color: '#c4b5fd' },
                { threshold: 45000, rate: 32.5, color: '#a78bfa' },
                { threshold: 120000, rate: 37, color: '#8b5cf6' },
                { threshold: 180000, rate: 45, color: '#7c3aed' }
            ],
            '2021–22': [
                { threshold: 0, rate: 0, color: '#f4f0fe' },
                { threshold: 18200, rate: 19, color: '#c4b5fd' },
                { threshold: 45000, rate: 32.5, color: '#a78bfa' },
                { threshold: 120000, rate: 37, color: '#8b5cf6' },
                { threshold: 180000, rate: 45, color: '#7c3aed' }
            ],
            '2022–23': [
                { threshold: 0, rate: 0, color: '#f4f0fe' },
                { threshold: 18200, rate: 19, color: '#c4b5fd' },
                { threshold: 45000, rate: 32.5, color: '#a78bfa' },
                { threshold: 120000, rate: 37, color: '#8b5cf6' },
                { threshold: 180000, rate: 45, color: '#7c3aed' }
            ],
            '2023–24': [
                { threshold: 0, rate: 0, color: '#f4f0fe' },
                { threshold: 18200, rate: 19, color: '#c4b5fd' },
                { threshold: 45000, rate: 32.5, color: '#a78bfa' },
                { threshold: 120000, rate: 37, color: '#8b5cf6' },
                { threshold: 180000, rate: 45, color: '#7c3aed' }
            ],
            '2024–25': [
                { threshold: 0, rate: 0, color: '#f4f0fe' },
                { threshold: 18200, rate: 16, color: '#c4b5fd' },
                { threshold: 45000, rate: 30, color: '#a78bfa' },
                { threshold: 135000, rate: 37, color: '#8b5cf6' },
                { threshold: 190000, rate: 45, color: '#7c3aed' }
            ],
            '2025–26': [
                { threshold: 0, rate: 0, color: '#f4f0fe' },
                { threshold: 18200, rate: 16, color: '#c4b5fd' },
                { threshold: 45000, rate: 30, color: '#a78bfa' },
                { threshold: 135000, rate: 37, color: '#8b5cf6' },
                { threshold: 190000, rate: 45, color: '#7c3aed' }
            ]
        };
        
        // Function to update tax brackets visualisation
        function updateTaxBrackets(year) {
            const brackets = taxBrackets[year];
            if (!brackets) return;
            
            const viz = document.getElementById('taxBracketsViz');
            viz.innerHTML = '';
            
            // Create bar container
            const barContainer = document.createElement('div');
            barContainer.className = 'tax-bracket-bar';
            
            // Create labels container
            const labelsContainer = document.createElement('div');
            labelsContainer.className = 'tax-bracket-labels';
            
            const maxIncome = 200000; // Cap visualisation at $200k
            
            brackets.forEach((bracket, i) => {
                const nextBracket = brackets[i + 1];
                const start = bracket.threshold;
                const end = nextBracket ? Math.min(nextBracket.threshold, maxIncome) : maxIncome;
                const width = ((end - start) / maxIncome) * 100;
                
                if (width > 0) {
                    // Create bracket segment
                    const div = document.createElement('div');
                    div.className = 'tax-bracket';
                    div.style.width = width + '%';
                    div.style.backgroundColor = bracket.color;
                    div.textContent = bracket.rate + '%';
                    barContainer.appendChild(div);
                    
                    // Create threshold label - only for major thresholds to avoid overlap
                    if (i === 0 || bracket.threshold === 18200 || bracket.threshold === 37000 || 
                        bracket.threshold === 45000 || bracket.threshold === 80000 || 
                        bracket.threshold === 87000 || bracket.threshold === 90000 || 
                        bracket.threshold === 120000 || bracket.threshold === 135000 ||
                        bracket.threshold === 180000 || bracket.threshold === 190000) {
                        const label = document.createElement('div');
                        label.className = 'tax-bracket-label';
                        const position = (start / maxIncome) * 100;
                        // Adjust position for labels near the end to prevent overlap
                        if (position > 85) {
                            label.style.right = (100 - position) + '%';
                            label.style.transform = 'none';
                        } else {
                            label.style.left = position + '%';
                        }
                        label.textContent = bracket.threshold === 0 ? '$0' : '$' + (bracket.threshold / 1000) + 'k';
                        labelsContainer.appendChild(label);
                    }
                }
            });
            
            // Add final threshold if needed
            const lastBracket = brackets[brackets.length - 1];
            if (lastBracket && lastBracket.threshold < maxIncome) {
                const label = document.createElement('div');
                label.className = 'tax-bracket-label';
                label.style.left = '100%';
                label.textContent = '$200k+';
                labelsContainer.appendChild(label);
            }
            
            viz.appendChild(barContainer);
            viz.appendChild(labelsContainer);
        }
        
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
        
        // URL parameter handling
        function getURLParams() {
            const params = new URLSearchParams(window.location.search);
            
            // Map short parameter names to full values
            const colorByMap = {
                'n': 'none',
                'a': 'age_range_display', 
                's': 'sex',
                't': 'taxable_status'
            };
            
            const totalByMap = {
                'ind': 'individuals_count',
                'inc': 'total_income_amount',
                'tax': 'net_tax_amount'
            };
            
            return {
                colorBy: colorByMap[params.get('c')] || 'age_range_display',
                totalBy: totalByMap[params.get('m')] || 'net_tax_amount',
                stack: params.get('st') !== '0',  // default true, 0 = false
                percentage: params.get('p') !== '0',  // default true, 0 = false
                cumulative: params.get('cu') !== '0',  // default true, 0 = false
                log: params.get('l') === '1',  // default false, 1 = true
                inflation: params.get('i') === '1',  // default false, 1 = true
                year: params.get('y') || years[0]
            };
        }
        
        function updateURLParams() {
            const params = new URLSearchParams();
            
            // Map full values to short parameter names
            const colorByReverseMap = {
                'none': 'n',
                'age_range_display': 'a',
                'sex': 's',
                'taxable_status': 't'
            };
            
            const totalByReverseMap = {
                'individuals_count': 'ind',
                'total_income_amount': 'inc',
                'net_tax_amount': 'tax'
            };
            
            const colorBy = document.getElementById('colorBy').value;
            const totalBy = document.getElementById('totalBy').value;
            
            // Only add parameters that differ from defaults
            if (colorBy !== 'age_range_display') {
                params.set('c', colorByReverseMap[colorBy]);
            }
            if (totalBy !== 'net_tax_amount') {
                params.set('m', totalByReverseMap[totalBy]);
            }
            if (!document.getElementById('stackToggle').checked) {
                params.set('st', '0');
            }
            if (!document.getElementById('percentageToggle').checked) {
                params.set('p', '0');
            }
            if (!document.getElementById('cumulativeToggle').checked) {
                params.set('cu', '0');
            }
            if (document.getElementById('logToggle').checked) {
                params.set('l', '1');
            }
            if (document.getElementById('inflationToggle').checked) {
                params.set('i', '1');
            }
            if (years[currentFrame] !== years[0]) {
                params.set('y', years[currentFrame]);
            }
            
            const newURL = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
            window.history.replaceState({}, '', newURL);
        }
        
        // Initialize from URL parameters
        const urlParams = getURLParams();
        document.getElementById('colorBy').value = urlParams.colorBy;
        document.getElementById('totalBy').value = urlParams.totalBy;
        document.getElementById('stackToggle').checked = urlParams.stack;
        document.getElementById('percentageToggle').checked = urlParams.percentage;
        document.getElementById('cumulativeToggle').checked = urlParams.cumulative;
        document.getElementById('logToggle').checked = urlParams.log;
        document.getElementById('inflationToggle').checked = urlParams.inflation;
        
        // Find the year index
        const yearIndex = years.indexOf(urlParams.year);
        currentFrame = yearIndex >= 0 ? yearIndex : 0;
        
        // Update stack icon based on initial state
        document.getElementById('stackIcon').textContent = urlParams.stack ? '≡' : '⦀';
        
        // Initialize chart with URL parameters
        updateChart(currentFrame, urlParams.colorBy, urlParams.stack ? 'stack' : 'group');
        updateNavButtons();
        updateURLParams();
        
        // Handle slider events
        document.getElementById('chart').on('plotly_sliderchange', function(eventdata) {
            if (!isPlaying) {  // Only respond to manual slider changes
                currentFrame = eventdata.slider.active;
                const stackMode = document.getElementById('stackToggle').checked ? 'stack' : 'group';
                updateChart(currentFrame, document.getElementById('colorBy').value, stackMode);
                updateNavButtons();
                updateURLParams();
            }
        });
        
        // Add keyboard navigation
        document.addEventListener('keydown', function(event) {
            // Only ignore text inputs, not selects or checkboxes
            if (event.target.tagName === 'INPUT' && event.target.type !== 'checkbox') return;
            
            const stackMode = document.getElementById('stackToggle').checked ? 'stack' : 'group';
            const colorBy = document.getElementById('colorBy').value;
            
            if (event.key === 'ArrowLeft' || event.key === 'Left') {
                event.preventDefault();
                if (currentFrame > 0) {
                    currentFrame--;
                    updateChart(currentFrame, colorBy, stackMode);
                    updateNavButtons();
                    updateURLParams();
                }
            } else if (event.key === 'ArrowRight' || event.key === 'Right') {
                event.preventDefault();
                if (currentFrame < years.length - 1) {
                    currentFrame++;
                    updateChart(currentFrame, colorBy, stackMode);
                    updateNavButtons();
                    updateURLParams();
                }
            }
        });
        
        // Handle window resize for responsive legend
        window.addEventListener('resize', function() {
            const stackMode = document.getElementById('stackToggle').checked ? 'stack' : 'group';
            const colorBy = document.getElementById('colorBy').value;
            updateChart(currentFrame, colorBy, stackMode);
        });
        
        // Mobile navigation buttons
        document.getElementById('prevYear').addEventListener('click', function() {
            const stackMode = document.getElementById('stackToggle').checked ? 'stack' : 'group';
            const colorBy = document.getElementById('colorBy').value;
            
            if (currentFrame > 0) {
                currentFrame--;
                updateChart(currentFrame, colorBy, stackMode);
                updateNavButtons();
                updateURLParams();
            }
        });
        
        document.getElementById('nextYear').addEventListener('click', function() {
            const stackMode = document.getElementById('stackToggle').checked ? 'stack' : 'group';
            const colorBy = document.getElementById('colorBy').value;
            
            if (currentFrame < years.length - 1) {
                currentFrame++;
                updateChart(currentFrame, colorBy, stackMode);
                updateNavButtons();
                updateURLParams();
            }
        });
        
// Update navigation button states
function updateNavButtons() {
    document.getElementById('prevYear').disabled = currentFrame === 0;
    document.getElementById('nextYear').disabled = currentFrame === years.length - 1;
}

// Initialize nav button states
updateNavButtons();

// Force resize on mobile after first render to fix slider text cutoff
if (window.innerWidth <= 768) {
    let resizeTriggered = false;
    document.getElementById('chart').on('plotly_afterplot', function() {
        if (!resizeTriggered) {
            resizeTriggered = true;
            window.dispatchEvent(new Event('resize'));
        }
    });
}

// Modal functionality
const modal = document.getElementById('helpModal');
const helpBtn = document.getElementById('helpButton');
const helpBtnMobile = document.getElementById('helpButtonMobile');
const closeBtn = document.getElementById('modalClose');

helpBtn.onclick = function() {
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
}

// Also handle mobile help button
if (helpBtnMobile) {
    helpBtnMobile.onclick = function() {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }
}

closeBtn.onclick = function() {
    modal.style.display = 'none';
    document.body.style.overflow = ''; // Restore scrolling
}

// Close modal when clicking outside of it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = 'none';
        document.body.style.overflow = ''; // Restore scrolling
    }
}

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' && modal.style.display === 'block') {
        modal.style.display = 'none';
        document.body.style.overflow = ''; // Restore scrolling
    }
});

// Open modal with shift + ? (which is just ?)
document.addEventListener('keydown', function(event) {
    if (event.key === '?' && modal.style.display !== 'block') {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }
});

} // End of initChart function'''
    
    # Create public directory if it doesn't exist
    import os
    os.makedirs('public', exist_ok=True)
    
    # Write the HTML file
    with open('public/index.html', 'w') as f:
        f.write(html_content)
    
    # Write the JavaScript file
    with open('public/script.js', 'w') as f:
        f.write(script_content)
    
    print("✓ Created Plotly-based animated chart: public/index.html")
    print("✓ Features:")
    print("  - Responsive design that fills the screen")
    print("  - Plotly stacked/grouped bar chart")
    print("  - Year slider with scrubbing capability")
    print("  - Colour by Gender, Taxable Status, or Age Group")
    print("  - Play/pause animation")
    print("  - Real-time statistics display")

if __name__ == '__main__':
    main()