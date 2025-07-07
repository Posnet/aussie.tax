#!/usr/bin/env python3
"""
Check for duplicate income ranges and understand why there's both 
"$250,001 or more" and "$250,001 to $500,000" ranges.
"""

import pandas as pd

def main():
    # Load the data
    df = pd.read_csv('ato_individual_tax_stats_by_demographics_2010_2023.csv')
    
    print("=== Checking income ranges containing 250,001 ===")
    
    # Find all ranges containing 250,001
    ranges_250k = df[df['taxable_income_range'].str.contains('250,001', na=False)]['taxable_income_range'].unique()
    print(f"\nFound {len(ranges_250k)} unique ranges containing '250,001':")
    for r in sorted(ranges_250k):
        print(f"  {r}")
    
    # Check which years have each range
    print("\n=== Years where each range appears ===")
    for range_val in sorted(ranges_250k):
        years = df[df['taxable_income_range'] == range_val]['income_year'].unique()
        print(f"\n{range_val}:")
        print(f"  Years: {sorted(years)}")
        print(f"  Count: {len(years)} years")
    
    # Check if they appear in the same year
    print("\n=== Checking if both ranges appear in same years ===")
    df_250k = df[df['taxable_income_range'].str.contains('250,001', na=False)]
    
    for year in sorted(df_250k['income_year'].unique()):
        year_data = df_250k[df_250k['income_year'] == year]
        ranges_in_year = year_data['taxable_income_range'].unique()
        if len(ranges_in_year) > 1:
            print(f"\n{year} has MULTIPLE 250k+ ranges:")
            for r in sorted(ranges_in_year):
                count = len(year_data[year_data['taxable_income_range'] == r])
                print(f"  {r} - {count} rows")
    
    # Look at the tax bracket changes over time
    print("\n=== Understanding the change ===")
    print("This likely reflects changes in tax brackets over the years.")
    print("Earlier years may have used '$250,001 or more' as the top bracket,")
    print("while later years introduced more granular brackets like '$250,001 to $500,000'")
    print("and '$500,001 to $1,000,000', etc.")

if __name__ == '__main__':
    main()