#!/usr/bin/env python3
"""
Investigate the specific rows with '$250,001 or more' to understand 
why they exist alongside the more specific ranges.
"""

import pandas as pd

def main():
    # Load the data
    df = pd.read_csv('ato_individual_tax_stats_by_demographics_2010_2023.csv')
    
    # Look at the specific rows with '$250,001 or more'
    df_250k_plus = df[df['taxable_income_range'] == 'Y00250001. $250,001 or more']
    
    print("=== All rows with '$250,001 or more' ===")
    print(f"Total rows: {len(df_250k_plus)}")
    
    # Show all the rows to understand the pattern
    cols_to_show = ['income_year', 'sex', 'taxable_status', 'age_range', 'taxable_income_range', 'individuals_count']
    print("\nAll occurrences:")
    print(df_250k_plus[cols_to_show].to_string())
    
    # Check if these are related to age ranges
    print("\n=== Pattern Analysis ===")
    print("Age ranges for '$250,001 or more':")
    print(df_250k_plus['age_range'].value_counts())
    
    print("\nSex distribution:")
    print(df_250k_plus['sex'].value_counts())
    
    print("\nTaxable status:")
    print(df_250k_plus['taxable_status'].value_counts())
    
    # Compare with regular 250k-500k range for same years
    print("\n=== Comparing with $250,001 to $500,000 for 2022-23 ===")
    df_2023 = df[df['income_year'] == '2022-23']
    
    # Get both ranges
    df_250_500k = df_2023[df_2023['taxable_income_range'] == 'B00250001. $250,001 to $500,000']
    df_250k_plus_2023 = df_2023[df_2023['taxable_income_range'] == 'Y00250001. $250,001 or more']
    
    print(f"\n$250,001 to $500,000: {len(df_250_500k)} rows")
    print(f"Age ranges: {sorted(df_250_500k['age_range'].unique())}")
    
    print(f"\n$250,001 or more: {len(df_250k_plus_2023)} rows")
    print(f"Age ranges: {sorted(df_250k_plus_2023['age_range'].unique())}")

if __name__ == '__main__':
    main()