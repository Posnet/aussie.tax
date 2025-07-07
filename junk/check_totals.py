#!/usr/bin/env python3
"""
Check total number of taxpayers in the Australian tax data.
"""

import pandas as pd

def main():
    # Load the individual data
    df = pd.read_csv('ato_individual_tax_stats_by_demographics_2010_2023.csv')
    
    # Also load the aggregate data to compare
    agg_df = pd.read_csv('ato_tax_stats_aggregates_2010_2023.csv')
    
    print("=== Checking total taxpayers by year ===\n")
    
    # For each year, sum up all individuals
    years = sorted(df['income_year'].unique())
    
    for year in years:
        year_data = df[df['income_year'] == year]
        
        # Sum individuals by major categories to avoid double counting
        # We need to be careful not to double count - let's check unique combinations
        print(f"\n{year}:")
        print("-" * 50)
        
        # Get unique combinations of sex, taxable status, age range, income range
        by_sex = year_data.groupby('sex')['individuals_count'].sum()
        print("By sex:")
        for sex, count in by_sex.items():
            print(f"  {sex}: {count:,.0f}")
        print(f"  Total: {by_sex.sum():,.0f}")
        
        # Check by taxable status
        by_taxable = year_data.groupby('taxable_status')['individuals_count'].sum()
        print("\nBy taxable status:")
        for status, count in by_taxable.items():
            print(f"  {status}: {count:,.0f}")
        print(f"  Total: {by_taxable.sum():,.0f}")
        
        # The issue might be that we're counting each person multiple times
        # Let's look at a specific combination
        sample = year_data[
            (year_data['sex'] == 'Female') & 
            (year_data['taxable_status'] == 'Taxable') &
            (year_data['age_range'] == '25 - 29')
        ]
        print(f"\nSample - Female, Taxable, 25-29 age group:")
        print(f"  Number of income ranges: {len(sample)}")
        print(f"  Total individuals: {sample['individuals_count'].sum():,.0f}")
    
    print("\n\n=== Aggregate data check ===")
    print(agg_df[['income_year', 'sex', 'taxable_status', 'age_range', 'taxable_income_range', 'individuals_count']])
    
    # Let's check the actual structure of the data
    print("\n\n=== Data structure analysis ===")
    print(f"Total rows in dataset: {len(df):,}")
    print(f"Unique years: {len(df['income_year'].unique())}")
    print(f"Unique sex values: {df['sex'].unique()}")
    print(f"Unique taxable status: {df['taxable_status'].unique()}")
    print(f"Unique age ranges: {len(df['age_range'].unique())}")
    print(f"Unique income ranges: {len(df['taxable_income_range'].unique())}")
    
    # Check if each row represents a unique group
    print("\n=== Checking 2022-23 specifically ===")
    df_2023 = df[df['income_year'] == '2022-23']
    
    # Each row should be a unique combination of demographics
    # A person belongs to ONE sex, ONE taxable status, ONE age range, and ONE income range
    # So we need to sum across all combinations
    total_2023 = df_2023['individuals_count'].sum()
    print(f"Total individuals in 2022-23 (summing all rows): {total_2023:,.0f}")
    
    # But this counts each person multiple times! Let's think differently
    # Actually, each row IS unique - a person can only be in one income bracket
    # So the sum should be correct if we sum within each sex/taxable status combination
    
    print("\n=== Correct calculation for 2022-23 ===")
    # For each sex and taxable status combination
    for sex in ['Female', 'Male']:
        for status in ['Taxable', 'Non Taxable']:
            subset = df_2023[
                (df_2023['sex'] == sex) & 
                (df_2023['taxable_status'] == status)
            ]
            total = subset['individuals_count'].sum()
            print(f"{sex} - {status}: {total:,.0f}")

if __name__ == '__main__':
    main()