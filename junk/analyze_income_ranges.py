#!/usr/bin/env python3
"""
Analyze income range variations across years to understand normalization needs.
"""

import pandas as pd
from collections import defaultdict

def main():
    # Load the data
    df = pd.read_csv('ato_individual_tax_stats_by_demographics_2010_2023.csv')
    
    print("=== Analyzing Income Range Variations Across Years ===\n")
    
    # Get unique income ranges per year
    ranges_by_year = defaultdict(set)
    for year in sorted(df['income_year'].unique()):
        year_ranges = df[df['income_year'] == year]['taxable_income_range'].dropna().unique()
        ranges_by_year[year] = set(year_ranges)
    
    # Find ranges that don't appear in all years
    all_ranges = set()
    for ranges in ranges_by_year.values():
        all_ranges.update(ranges)
    
    print(f"Total unique income ranges across all years: {len(all_ranges)}")
    
    # Check which ranges appear in which years
    print("\n=== Ranges that don't appear in all years ===")
    for range_val in sorted(all_ranges):
        years_with_range = []
        for year, ranges in ranges_by_year.items():
            if range_val in ranges:
                years_with_range.append(year)
        
        if len(years_with_range) < len(ranges_by_year):
            print(f"\n{range_val}")
            print(f"  Appears in {len(years_with_range)}/{len(ranges_by_year)} years")
            print(f"  Years: {sorted(years_with_range)}")
    
    # Analyze the problematic ranges
    print("\n\n=== Key Issues to Address ===")
    
    # 1. Tax bracket changes
    print("\n1. Tax Bracket Changes:")
    print("   - $10,001 to $15,000 vs $10,001 to $18,200")
    print("   - $15,001 to $20,000 vs $18,201 to $25,000")
    print("   - Various brackets in $37k-50k range")
    print("   - Various brackets in $60k-70k range")
    print("   - Various brackets in $80k-90k range")
    print("   - Various brackets in $100k-150k range")
    
    # 2. Under 18 high earners
    print("\n2. Under 18 High Earners:")
    under18_250plus = df[
        (df['age_range'] == '00. Under 18') & 
        (df['taxable_income_range'] == 'Y00250001. $250,001 or more')
    ]
    print(f"   - {len(under18_250plus)} rows with 'Under 18' + '$250,001 or more'")
    print(f"   - Total individuals affected: {under18_250plus['individuals_count'].sum():.0f}")
    
    # 3. Check for overlapping ranges
    print("\n3. Overlapping/Conflicting Ranges:")
    sorted_ranges = sorted(all_ranges)
    for i, r1 in enumerate(sorted_ranges):
        for r2 in sorted_ranges[i+1:]:
            # Simple check for obvious overlaps
            if '$250,001 or more' in r1 and '$250,001 to' in r2:
                print(f"   - '{r1}' overlaps with '{r2}'")
    
    # Propose normalized ranges
    print("\n\n=== Proposed Normalized Income Ranges ===")
    normalized_ranges = [
        "$6,000 or less",
        "$6,001 to $10,000",
        "$10,001 to $20,000",      # Combine $10k-15k, $15k-20k, $10k-18.2k, $18.2k-20k
        "$20,001 to $30,000",      # Combine $20k-25k and $25k-30k
        "$30,001 to $40,000",      # Combine $30k-37k and $37k-40k
        "$40,001 to $50,000",      # Combine all $40k-50k variations
        "$50,001 to $60,000",      # $50k-55k and $55k-60k
        "$60,001 to $80,000",      # Combine $60k-70k and $70k-80k variations
        "$80,001 to $100,000",     # Combine $80k-90k and $90k-100k variations
        "$100,001 to $150,000",    # Combine all $100k-150k variations
        "$150,001 to $200,000",    # Combine $150k-180k and $180k-200k
        "$200,001 to $250,000",    # Keep as is
        "$250,001 to $500,000",    # Keep as is
        "$500,001 to $1,000,000",  # Keep as is
        "$1,000,001 or more"       # Keep as is
    ]
    
    for i, r in enumerate(normalized_ranges):
        print(f"{i+1:2d}. {r}")

if __name__ == '__main__':
    main()