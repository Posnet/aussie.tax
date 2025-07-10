#!/usr/bin/env python3
"""
Create inflation-adjusted dataset by redistributing historical data into 2023-equivalent income brackets.
This shows how people earning equivalent purchasing power fared across different years.
"""

import pandas as pd
import numpy as np

# Inflation factors relative to 2022-23
inflation_factors = {
    '2010–11': 1.34,
    '2011–12': 1.31,
    '2012–13': 1.28,
    '2013–14': 1.25,
    '2014–15': 1.23,
    '2015–16': 1.21,
    '2016–17': 1.19,
    '2017–18': 1.17,
    '2018–19': 1.15,
    '2019–20': 1.14,
    '2020–21': 1.12,
    '2021–22': 1.07,
    '2022–23': 1.00
}

# Modern income brackets (2023 dollars) - these will be our target brackets
modern_brackets = [
    (0, 6000, '$6,000 or less'),
    (6001, 10000, '$6,001 to $10,000'),
    (10001, 20000, '$10,001 to $20,000'),
    (20001, 30000, '$20,001 to $30,000'),
    (30001, 40000, '$30,001 to $40,000'),
    (40001, 50000, '$40,001 to $50,000'),
    (50001, 60000, '$50,001 to $60,000'),
    (60001, 80000, '$60,001 to $80,000'),
    (80001, 100000, '$80,001 to $100,000'),
    (100001, 150000, '$100,001 to $150,000'),
    (150001, 200000, '$150,001 to $200,000'),
    (200001, 250000, '$200,001 to $250,000'),
    (250001, 500000, '$250,001 to $500,000'),
    (500001, 1000000, '$500,001 to $1,000,000'),
    (1000001, float('inf'), '$1,000,001 or more')
]

def get_bracket_bounds(bracket_label):
    """Extract numeric bounds from bracket labels."""
    if bracket_label == '$6,000 or less':
        return 0, 6000
    elif bracket_label == '$1,000,001 or more':
        return 1000001, 2000000  # Use 2M as practical upper bound
    else:
        # Parse strings like '$20,001 to $30,000'
        parts = bracket_label.replace('$', '').replace(',', '').split(' to ')
        return int(parts[0]), int(parts[1])

def calculate_overlap(source_min, source_max, target_min, target_max):
    """Calculate what fraction of source bracket overlaps with target bracket."""
    # No overlap
    if source_max <= target_min or source_min >= target_max:
        return 0.0
    
    # Calculate overlap
    overlap_min = max(source_min, target_min)
    overlap_max = min(source_max, target_max)
    
    # Fraction of source bracket that falls in target bracket
    # Using uniform distribution assumption
    source_width = source_max - source_min
    if source_width == 0:
        return 0.0
    
    overlap_width = overlap_max - overlap_min
    return overlap_width / source_width

def redistribute_year_data(year_df, year, inflation_factor):
    """Redistribute one year's data into modern brackets based on inflation adjustment."""
    
    redistributed_rows = []
    
    # Group by all categorical variables to preserve demographics
    groupby_cols = ['income_range_display', 'sex', 'taxable_status', 'age_range_display']
    
    for group_keys, group_df in year_df.groupby(groupby_cols):
        source_bracket_label = group_keys[0]
        sex = group_keys[1]
        taxable_status = group_keys[2]
        age_range = group_keys[3]
        
        # Get source bracket bounds in nominal dollars
        source_min_nominal, source_max_nominal = get_bracket_bounds(source_bracket_label)
        
        # Convert to 2023 dollars
        source_min_2023 = source_min_nominal * inflation_factor
        source_max_2023 = source_max_nominal * inflation_factor
        
        # Get totals for this demographic group
        total_individuals = group_df['individuals_count'].sum()
        total_income = group_df['total_income_amount'].sum()
        total_tax = group_df['net_tax_amount'].sum()
        
        # Redistribute into modern brackets
        for target_min, target_max, target_label in modern_brackets:
            overlap = calculate_overlap(source_min_2023, source_max_2023, target_min, target_max)
            
            if overlap > 0:
                # Allocate proportional share to this target bracket
                new_row = {
                    'income_year': year,
                    'normalized_income_range': target_label,
                    'income_range_display': target_label,
                    'sex': sex,
                    'taxable_status': taxable_status,
                    'age_range_display': age_range,
                    # Note: do NOT inflate individuals count - round to nearest integer
                    'individuals_count': round(total_individuals * overlap),
                    # DO inflate income and tax amounts
                    'total_income_amount': total_income * overlap * inflation_factor,
                    'net_tax_amount': total_tax * overlap * inflation_factor
                }
                redistributed_rows.append(new_row)
    
    return pd.DataFrame(redistributed_rows)

def main():
    # Load original data
    print("Loading original data...")
    df = pd.read_csv('ato_2010-2023.csv')
    
    # Process each year
    all_redistributed = []
    
    for year in df['income_year'].unique():
        print(f"\nProcessing {year}...")
        
        year_df = df[df['income_year'] == year]
        inflation_factor = inflation_factors.get(year, 1.0)
        
        if year == '2022–23':
            # For 2022-23, no redistribution needed - it's already in 2023 dollars
            year_redistributed = year_df.copy()
        else:
            # Redistribute historical data
            year_redistributed = redistribute_year_data(year_df, year, inflation_factor)
        
        all_redistributed.append(year_redistributed)
        
        # Print summary
        orig_total = year_df['individuals_count'].sum()
        new_total = year_redistributed['individuals_count'].sum()
        print(f"  Original total individuals: {orig_total:,.0f}")
        print(f"  Redistributed total: {new_total:,.0f}")
        print(f"  Difference: {abs(orig_total - new_total):,.0f} ({abs(orig_total - new_total)/orig_total*100:.2f}%)")
    
    # Combine all years
    final_df = pd.concat(all_redistributed, ignore_index=True)
    
    # Group by the same columns and sum to consolidate any duplicate rows
    groupby_columns = [
        'income_year',
        'normalized_income_range', 
        'income_range_display',
        'sex',
        'taxable_status',
        'age_range_display'
    ]
    
    final_df = final_df.groupby(groupby_columns, as_index=False).agg({
        'individuals_count': 'sum',
        'total_income_amount': 'sum',
        'net_tax_amount': 'sum'
    })
    
    # Save the redistributed dataset
    final_df.to_csv('ato_2010-2023_inflation_redistributed.csv', index=False)
    
    print("\n" + "="*60)
    print("Redistribution complete!")
    print(f"Output saved to: ato_2010-2023_inflation_redistributed.csv")
    print(f"Total rows: {len(final_df):,}")
    
    # Verify a specific bracket across years
    print("\nExample: People earning $80,001-$100,000 (in 2023 dollars) across years:")
    example_bracket = final_df[final_df['normalized_income_range'] == '$80,001 to $100,000']
    
    for year in sorted(example_bracket['income_year'].unique()):
        year_data = example_bracket[example_bracket['income_year'] == year]
        total_people = year_data['individuals_count'].sum()
        total_income = year_data['total_income_amount'].sum()
        total_tax = year_data['net_tax_amount'].sum()
        
        if total_income > 0:
            effective_rate = (total_tax / total_income) * 100
            avg_income = total_income / total_people if total_people > 0 else 0
            
            print(f"\n  {year}:")
            print(f"    People: {total_people:,.0f}")
            print(f"    Avg income: ${avg_income:,.0f}")
            print(f"    Effective tax rate: {effective_rate:.1f}%")

if __name__ == '__main__':
    main()