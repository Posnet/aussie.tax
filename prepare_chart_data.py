#!/usr/bin/env python3
"""
Prepare data for the animated tax visualization chart.
"""

import pandas as pd
import json

def simplify_income_range(val):
    """Remove the sorting prefix for display."""
    if pd.isna(val):
        return val
    # Remove prefixes like 'A00006000. ' or 'B00250001. '
    if '. ' in str(val):
        return str(val).split('. ', 1)[1]
    return str(val)

def simplify_age_range(val):
    """Remove the sorting prefix for display."""
    if pd.isna(val):
        return val
    # Remove prefixes like '00. ' or '12. '
    if '. ' in str(val):
        return str(val).split('. ', 1)[1]
    return str(val)

def main():
    # Load the data
    df = pd.read_csv('ato_individual_tax_stats_by_demographics_2010_2023.csv')
    
    # Create display-friendly versions of the ranges
    df['income_range_display'] = df['taxable_income_range'].apply(simplify_income_range)
    df['age_range_display'] = df['age_range'].apply(simplify_age_range)
    
    # Select relevant columns for the visualization
    viz_cols = [
        'income_year', 'sex', 'taxable_status', 'age_range', 'age_range_display',
        'taxable_income_range', 'income_range_display', 'individuals_count',
        'total_income_amount', 'net_tax_amount'
    ]
    
    viz_df = df[viz_cols].copy()
    
    # Remove rows with missing individual counts
    viz_df = viz_df.dropna(subset=['individuals_count'])
    
    # Convert to records for JSON
    records = viz_df.to_dict(orient='records')
    
    # Create summary statistics for the visualization
    summary = {
        'years': sorted(viz_df['income_year'].unique()),
        'income_ranges': sorted(viz_df['taxable_income_range'].unique()),
        'income_ranges_display': [simplify_income_range(r) for r in sorted(viz_df['taxable_income_range'].unique())],
        'age_ranges': sorted(viz_df['age_range'].unique()),
        'age_ranges_display': [simplify_age_range(r) for r in sorted(viz_df['age_range'].unique())],
        'total_records': len(records)
    }
    
    # Save as JSON for embedding
    with open('chart_data.json', 'w') as f:
        json.dump({
            'data': records,
            'summary': summary
        }, f, indent=2)
    
    print(f"✓ Prepared {len(records):,} records for visualization")
    print(f"✓ Years: {summary['years'][0]} to {summary['years'][-1]}")
    print(f"✓ Income ranges: {len(summary['income_ranges'])}")
    print(f"✓ Age ranges: {len(summary['age_ranges'])}")
    print("✓ Saved to chart_data.json")

if __name__ == '__main__':
    main()