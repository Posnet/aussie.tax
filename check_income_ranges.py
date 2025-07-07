#!/usr/bin/env python3
"""
Check all unique income ranges to identify sorting issues.
"""

import pandas as pd

def main():
    # Load the data
    df = pd.read_csv('ato_individual_tax_stats_by_demographics_2010_2023.csv')
    
    print("=== All unique income ranges ===")
    income_ranges = sorted(df['taxable_income_range'].dropna().unique())
    
    for i, income_range in enumerate(income_ranges):
        print(f"{i:2d}: {income_range}")
    
    print("\n=== Problematic ranges that need fixing ===")
    print("- '$1,000,001 or more' should sort after '$500,001 to $1,000,000'")
    print("- Any 'or more' or 'or less' ranges need special handling")
    print("- 'all ranges' should sort last")

if __name__ == '__main__':
    main()