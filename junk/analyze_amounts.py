#!/usr/bin/env python3
"""
Analyze the net_tax_amount and total_income_amount columns to understand what they represent.
"""

import pandas as pd

def main():
    # Load the data
    df = pd.read_csv('ato_individual_tax_stats_by_demographics_2010_2023.csv')
    
    print("=== Understanding the Amount Columns ===\n")
    
    # Look at 2022-23 data
    df_2023 = df[df['income_year'] == '2022-23']
    
    # Sample some rows to see the values
    print("Sample rows showing individuals_count, total_income_amount, and net_tax_amount:")
    print("-" * 100)
    sample = df_2023[
        (df_2023['sex'] == 'Female') & 
        (df_2023['taxable_status'] == 'Taxable') &
        (df_2023['age_range'] == '30 - 34')
    ][['taxable_income_range', 'individuals_count', 'total_income_amount', 'net_tax_amount']].head(10)
    
    for _, row in sample.iterrows():
        print(f"Income range: {row['taxable_income_range']:<25} | "
              f"Individuals: {row['individuals_count']:>8,.0f} | "
              f"Total Income: ${row['total_income_amount']:>15,.0f} | "
              f"Net Tax: ${row['net_tax_amount']:>12,.0f}")
    
    # Calculate averages to understand the data better
    print("\n\n=== Calculating Averages to Understand the Data ===")
    print("-" * 100)
    
    for _, row in sample.iterrows():
        if row['individuals_count'] > 0:
            avg_income = row['total_income_amount'] / row['individuals_count']
            avg_tax = row['net_tax_amount'] / row['individuals_count']
            tax_rate = (row['net_tax_amount'] / row['total_income_amount'] * 100) if row['total_income_amount'] > 0 else 0
            
            print(f"Income range: {row['taxable_income_range']:<25}")
            print(f"  Average income per person: ${avg_income:>12,.2f}")
            print(f"  Average tax per person: ${avg_tax:>12,.2f}")
            print(f"  Effective tax rate: {tax_rate:>6.1f}%")
            print()
    
    # Check aggregate totals
    print("\n=== 2022-23 Aggregate Totals ===")
    print("-" * 100)
    
    total_individuals = df_2023['individuals_count'].sum()
    total_income = df_2023['total_income_amount'].sum()
    total_tax = df_2023['net_tax_amount'].sum()
    
    print(f"Total individuals: {total_individuals:,.0f}")
    print(f"Total income reported: ${total_income:,.0f}")
    print(f"Total net tax collected: ${total_tax:,.0f}")
    print(f"Average income per taxpayer: ${total_income/total_individuals:,.2f}")
    print(f"Average tax per taxpayer: ${total_tax/total_individuals:,.2f}")
    print(f"Overall effective tax rate: {total_tax/total_income*100:.2f}%")
    
    # Check taxable vs non-taxable
    print("\n\n=== Taxable vs Non-Taxable Analysis ===")
    print("-" * 100)
    
    taxable_df = df_2023[df_2023['taxable_status'] == 'Taxable']
    non_taxable_df = df_2023[df_2023['taxable_status'] == 'Non Taxable']
    
    print("Taxable individuals:")
    print(f"  Count: {taxable_df['individuals_count'].sum():,.0f}")
    print(f"  Total income: ${taxable_df['total_income_amount'].sum():,.0f}")
    print(f"  Total tax: ${taxable_df['net_tax_amount'].sum():,.0f}")
    
    print("\nNon-taxable individuals:")
    print(f"  Count: {non_taxable_df['individuals_count'].sum():,.0f}")
    print(f"  Total income: ${non_taxable_df['total_income_amount'].sum():,.0f}")
    print(f"  Total tax: ${non_taxable_df['net_tax_amount'].sum():,.0f}")
    
    # Check for any non-zero tax in non-taxable category
    non_taxable_with_tax = non_taxable_df[non_taxable_df['net_tax_amount'] > 0]
    if len(non_taxable_with_tax) > 0:
        print(f"\nWARNING: Found {len(non_taxable_with_tax)} rows where non-taxable individuals have tax > 0")

if __name__ == '__main__':
    main()