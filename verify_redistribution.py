#!/usr/bin/env python3
"""
Verify that the redistributed inflation-adjusted data maintains integrity:
1. Total individuals should remain the same (or very close due to rounding)
2. Total income should equal original total * inflation factor
3. Report on tax changes (which are expected due to bracket changes)
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

def verify_redistribution():
    # Load both datasets
    print("Loading datasets...")
    df_original = pd.read_csv('ato_2010-2023.csv')
    df_redistributed = pd.read_csv('ato_2010-2023_inflation_redistributed.csv')
    
    print("\nVerifying data integrity for each year:")
    print("=" * 100)
    
    all_years_valid = True
    
    for year in sorted(df_original['income_year'].unique()):
        print(f"\n{year}:")
        
        # Get data for this year
        orig_year = df_original[df_original['income_year'] == year]
        redis_year = df_redistributed[df_redistributed['income_year'] == year]
        
        # Get inflation factor
        inflation_factor = inflation_factors.get(year, 1.0)
        
        # Calculate totals
        orig_individuals = orig_year['individuals_count'].sum()
        redis_individuals = redis_year['individuals_count'].sum()
        
        orig_income = orig_year['total_income_amount'].sum()
        redis_income = redis_year['total_income_amount'].sum()
        
        orig_tax = orig_year['net_tax_amount'].sum()
        redis_tax = redis_year['net_tax_amount'].sum()
        
        # Expected values
        expected_individuals = orig_individuals
        expected_income = orig_income * inflation_factor
        
        # Calculate differences
        indiv_diff = redis_individuals - expected_individuals
        indiv_pct_diff = (indiv_diff / expected_individuals * 100) if expected_individuals > 0 else 0
        
        income_diff = redis_income - expected_income
        income_pct_diff = (income_diff / expected_income * 100) if expected_income > 0 else 0
        
        # Tax comparison (just for information)
        tax_change = redis_tax - (orig_tax * inflation_factor)
        tax_pct_change = (tax_change / (orig_tax * inflation_factor) * 100) if orig_tax > 0 else 0
        
        # Print results
        print(f"  Inflation factor: {inflation_factor}")
        print(f"\n  Individuals:")
        print(f"    Original:      {orig_individuals:15,.0f}")
        print(f"    Redistributed: {redis_individuals:15,.0f}")
        print(f"    Difference:    {indiv_diff:15,.0f} ({indiv_pct_diff:+.2f}%)")
        
        print(f"\n  Total Income:")
        print(f"    Original:      ${orig_income:18,.0f}")
        print(f"    Expected:      ${expected_income:18,.0f} (original × {inflation_factor})")
        print(f"    Redistributed: ${redis_income:18,.0f}")
        print(f"    Difference:    ${income_diff:18,.0f} ({income_pct_diff:+.2f}%)")
        
        print(f"\n  Tax (for reference - changes expected due to bracket redistribution):")
        print(f"    Original:      ${orig_tax:18,.0f}")
        print(f"    Inflated orig: ${orig_tax * inflation_factor:18,.0f} (original × {inflation_factor})")
        print(f"    Redistributed: ${redis_tax:18,.0f}")
        print(f"    Change:        ${tax_change:18,.0f} ({tax_pct_change:+.2f}%)")
        
        # Validation
        individuals_valid = abs(indiv_pct_diff) < 0.1  # Allow 0.1% difference due to rounding
        income_valid = abs(income_pct_diff) < 0.01  # Allow 0.01% difference due to floating point
        
        if not individuals_valid:
            print(f"\n  ⚠️  WARNING: Individual count difference exceeds 0.1%!")
            all_years_valid = False
            
        if not income_valid:
            print(f"\n  ⚠️  WARNING: Income total difference exceeds 0.01%!")
            all_years_valid = False
            
        if individuals_valid and income_valid:
            print(f"\n  ✓ Data integrity verified")
    
    # Summary
    print("\n" + "=" * 100)
    print("SUMMARY:")
    
    if all_years_valid:
        print("✓ All years pass validation!")
        print("  - Individual counts are preserved (within rounding tolerance)")
        print("  - Income totals are correctly inflated")
        print("  - Tax amounts have changed as expected due to bracket redistribution")
    else:
        print("❌ Some years failed validation - check warnings above")
    
    # Additional analysis - show bracket distribution changes
    print("\n" + "=" * 100)
    print("BRACKET DISTRIBUTION ANALYSIS (2010-11 vs 2022-23):")
    
    # Compare bracket distributions for first and last year
    first_year = '2010–11'
    last_year = '2022–23'
    
    orig_first = df_original[df_original['income_year'] == first_year].groupby('normalized_income_range')['individuals_count'].sum()
    redis_first = df_redistributed[df_redistributed['income_year'] == first_year].groupby('normalized_income_range')['individuals_count'].sum()
    
    print(f"\n{first_year} Bracket Distribution Changes:")
    print(f"{'Income Range':<25} {'Original':>15} {'Redistributed':>15} {'Change':>15}")
    print("-" * 75)
    
    # Get all brackets from both datasets
    all_brackets = sorted(set(orig_first.index) | set(redis_first.index), 
                         key=lambda x: int(x.replace('$', '').replace(',', '').split()[0]) if x != '$1,000,001 or more' else 9999999)
    
    for bracket in all_brackets:
        orig_count = orig_first.get(bracket, 0)
        redis_count = redis_first.get(bracket, 0)
        change = redis_count - orig_count
        print(f"{bracket:<25} {orig_count:15,.0f} {redis_count:15,.0f} {change:+15,.0f}")

if __name__ == '__main__':
    verify_redistribution()