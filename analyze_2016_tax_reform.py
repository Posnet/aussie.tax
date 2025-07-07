#!/usr/bin/env python3
"""
Analyze the 2016-17 tax reform impact on income distribution.

Key changes in 2016-17:
1. The 32.5% tax bracket upper threshold increased from $80,000 to $87,000
2. Income brackets were reorganized (e.g., $37-40K became $37-41K)
"""

import csv
import pandas as pd

# Load the data
print("Loading tax data...")
df = pd.read_csv('ato_individual_tax_stats_by_demographics_2010_2023.csv')

# Focus on key years
years = ['2014–15', '2015–16', '2016–17', '2017–18']
df_years = df[df['income_year'].isin(years)]

# Aggregate by income bracket
agg_data = df_years.groupby(['income_year', 'taxable_income_range'])['individuals_count'].sum().reset_index()

print("\n=== 2016-17 TAX REFORM ANALYSIS ===")
print("\nReform Details:")
print("- Effective July 1, 2016")
print("- 32.5% tax bracket upper threshold increased from $80,000 to $87,000")
print("- Tax rate on income $80,001-$87,000 reduced from 37% to 32.5%")
print("- ATO reorganized some income brackets (e.g., $37-40K → $37-41K)")

# Analyze the $37K threshold area
print("\n\n1. CHANGES AROUND $37,000 THRESHOLD")
print("=" * 50)

for year in years:
    year_data = agg_data[agg_data['income_year'] == year]
    
    # Count people in $30-50K range
    count_30_37 = year_data[year_data['taxable_income_range'].str.contains('30,001 to \\$37,000')]['individuals_count'].sum()
    count_37_40 = year_data[year_data['taxable_income_range'].str.contains('37,001 to \\$40,000')]['individuals_count'].sum()
    count_37_41 = year_data[year_data['taxable_income_range'].str.contains('37,001 to \\$41,000')]['individuals_count'].sum()
    count_40_45 = year_data[year_data['taxable_income_range'].str.contains('40,001 to \\$45,000')]['individuals_count'].sum()
    count_41_45 = year_data[year_data['taxable_income_range'].str.contains('41,001 to \\$45,000')]['individuals_count'].sum()
    count_45_50 = year_data[year_data['taxable_income_range'].str.contains('45,001 to \\$50,000')]['individuals_count'].sum()
    count_45_48 = year_data[year_data['taxable_income_range'].str.contains('45,001 to \\$48,000')]['individuals_count'].sum()
    
    print(f"\n{year}:")
    print(f"  $30,001-$37,000: {count_30_37:,.0f}")
    
    if count_37_40 > 0:
        print(f"  $37,001-$40,000: {count_37_40:,.0f}")
    if count_37_41 > 0:
        print(f"  $37,001-$41,000: {count_37_41:,.0f} ← New bracket from 2016-17")
        
    if count_40_45 > 0:
        print(f"  $40,001-$45,000: {count_40_45:,.0f}")
    if count_41_45 > 0:
        print(f"  $41,001-$45,000: {count_41_45:,.0f} ← New bracket from 2016-17")
        
    if count_45_50 > 0:
        print(f"  $45,001-$50,000: {count_45_50:,.0f}")
    if count_45_48 > 0:
        print(f"  $45,001-$48,000: {count_45_48:,.0f} ← New bracket from 2016-17")

# Calculate the shift
print("\nImpact of bracket reorganization:")
count_37_40_2015 = agg_data[(agg_data['income_year'] == '2015–16') & 
                            (agg_data['taxable_income_range'].str.contains('37,001 to \\$40,000'))]['individuals_count'].sum()
count_37_41_2016 = agg_data[(agg_data['income_year'] == '2016–17') & 
                            (agg_data['taxable_income_range'].str.contains('37,001 to \\$41,000'))]['individuals_count'].sum()

print(f"  2015-16: {count_37_40_2015:,.0f} people in $37-40K bracket")
print(f"  2016-17: {count_37_41_2016:,.0f} people in $37-41K bracket")
print(f"  Difference: +{count_37_41_2016 - count_37_40_2015:,.0f} people")
print(f"  This represents people earning $40-41K who moved into the lower bracket")

# Analyze the $80-87K threshold area
print("\n\n2. CHANGES AROUND $80,000-$87,000 THRESHOLD")
print("=" * 50)

for year in years:
    year_data = agg_data[agg_data['income_year'] == year]
    
    count_70_80 = year_data[year_data['taxable_income_range'].str.contains('70,001 to \\$80,000')]['individuals_count'].sum()
    count_80_87 = year_data[year_data['taxable_income_range'].str.contains('80,001 to \\$87,000')]['individuals_count'].sum()
    count_87_90 = year_data[year_data['taxable_income_range'].str.contains('87,001 to \\$90,000')]['individuals_count'].sum()
    count_90_100 = year_data[year_data['taxable_income_range'].str.contains('90,001 to \\$100,000')]['individuals_count'].sum()
    
    print(f"\n{year}:")
    print(f"  $70,001-$80,000: {count_70_80:,.0f}")
    print(f"  $80,001-$87,000: {count_80_87:,.0f} ← Tax rate reduced from 37% to 32.5% in 2016-17")
    print(f"  $87,001-$90,000: {count_87_90:,.0f}")
    print(f"  $90,001-$100,000: {count_90_100:,.0f}")

# Calculate year-over-year changes
print("\nYear-over-year changes in $80-87K bracket:")
for i in range(len(years)-1):
    year1 = years[i]
    year2 = years[i+1]
    
    count1 = agg_data[(agg_data['income_year'] == year1) & 
                      (agg_data['taxable_income_range'].str.contains('80,001 to \\$87,000'))]['individuals_count'].sum()
    count2 = agg_data[(agg_data['income_year'] == year2) & 
                      (agg_data['taxable_income_range'].str.contains('80,001 to \\$87,000'))]['individuals_count'].sum()
    
    change = count2 - count1
    pct_change = (change / count1 * 100) if count1 > 0 else 0
    
    print(f"  {year1} to {year2}: {change:+,.0f} ({pct_change:+.1f}%)")

print("\n\n3. TAX SAVINGS FOR AFFECTED TAXPAYERS")
print("=" * 50)
print("\nFor someone earning in the $80,001-$87,000 range:")
print("  Old rate (2015-16): 37% on income above $80,000")
print("  New rate (2016-17): 32.5% on income above $80,000")
print("  Tax savings: 4.5% of income above $80,000")
print("\nMaximum benefit (at $87,000 income):")
print("  Tax savings = ($87,000 - $80,000) × 4.5% = $315 per year")

count_80_87_2017 = agg_data[(agg_data['income_year'] == '2016–17') & 
                            (agg_data['taxable_income_range'].str.contains('80,001 to \\$87,000'))]['individuals_count'].sum()
print(f"\nNumber of people benefiting: {count_80_87_2017:,.0f} (in 2016-17)")
print(f"Estimated total tax reduction: ${count_80_87_2017 * 315 / 1_000_000:.1f} million")

print("\n\n4. SUMMARY")
print("=" * 50)
print("The 2016-17 tax reform had two main effects:")
print("1. Bracket reorganization: The $37-40K bracket became $37-41K, capturing")
print("   an additional ~153,000 people who were previously in higher brackets")
print("2. Tax reduction: ~498,000 people earning $80-87K received a tax cut")
print("   through the reduction in marginal rate from 37% to 32.5%")