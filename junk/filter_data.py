#!/usr/bin/env python3
"""
Filter Australian tax data to remove aggregate 'All' category rows
and save with more contextual filenames.
"""

import pandas as pd
import os

def main():
    # Load the cleaned data
    df = pd.read_csv('australian_tax_data_cleaned.csv')

    print('=== Filtering out All category rows ===')

    # Separate 'All' category rows (these are summary/aggregate rows)
    all_rows = df[
        (df['sex'] == 'All') | 
        (df['taxable_status'] == 'All') | 
        (df['age_range'] == 'all ranges')
    ]

    # Filter to individual-level data (no 'All' categories)
    filtered_df = df[
        (df['sex'] != 'All') & 
        (df['taxable_status'] != 'All') & 
        (df['age_range'] != 'all ranges')
    ]

    print(f'Original records: {len(df):,}')
    print(f'All category rows: {len(all_rows):,}')
    print(f'Filtered records: {len(filtered_df):,}')

    # Save All category rows separately
    all_rows.to_csv('ato_tax_stats_aggregates_2010_2023.csv', index=False)
    print('✓ Saved aggregate rows to: ato_tax_stats_aggregates_2010_2023.csv')

    # Save filtered data with contextual name
    filtered_df.to_csv('ato_individual_tax_stats_by_demographics_2010_2023.csv', index=False)
    print('✓ Saved individual data to: ato_individual_tax_stats_by_demographics_2010_2023.csv')

    # Remove old file
    if os.path.exists('australian_tax_data_cleaned.csv'):
        os.remove('australian_tax_data_cleaned.csv')
        print('✓ Removed old file: australian_tax_data_cleaned.csv')

    print('\n=== Filtered dataset summary ===')
    print('Years:', sorted(filtered_df['income_year'].unique()))
    print('Sex categories:', sorted(filtered_df['sex'].unique()))
    print('Taxable status:', sorted(filtered_df['taxable_status'].unique()))
    print('Age ranges:', sorted([x for x in filtered_df['age_range'].unique() if pd.notna(x)]))

    # Update JSON data for pivot table
    core_columns = [
        'income_year', 'sex', 'taxable_status', 'age_range', 'taxable_income_range',
        'individuals_count', 'total_income_amount', 'net_tax_amount'
    ]

    pivot_df = filtered_df[core_columns].copy()
    pivot_df = pivot_df.dropna(subset=['individuals_count'])

    json_data = pivot_df.to_json(orient='records')
    with open('tax_data.json', 'w') as f:
        f.write(json_data)

    print(f'✓ Updated tax_data.json with {len(pivot_df):,} records')

if __name__ == '__main__':
    main()