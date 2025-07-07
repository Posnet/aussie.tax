#!/usr/bin/env python3
"""
Analyze the 2016-17 tax bracket change where the 32.5% threshold upper limit
was raised from $80,000 to $87,000.
"""

import csv
import pandas as pd
import numpy as np

def normalize_to_10k_brackets(df):
    """Normalize data to $10K brackets for comparison"""
    # Define normalized brackets
    normalized_brackets = [
        (0, 10000), (10000, 20000), (20000, 30000), (30000, 40000),
        (40000, 50000), (50000, 60000), (60000, 70000), (70000, 80000),
        (80000, 90000), (90000, 100000), (100000, 110000), (110000, 120000),
        (120000, 130000), (130000, 140000), (140000, 150000), (150000, 200000),
        (200000, 250000), (250000, 500000), (500000, 1000000), (1000000, float('inf'))
    ]
    
    results = []
    
    for year in df['income_year'].unique():
        year_data = df[df['income_year'] == year]
        
        for low, high in normalized_brackets:
            count = 0
            
            # Map original brackets to normalized brackets
            for _, row in year_data.iterrows():
                bracket = row['taxable_income_range']
                individuals = row['individuals_count']
                
                # Parse bracket boundaries
                if '$' not in bracket:
                    continue
                    
                # Extract min/max values from bracket string
                if ' or less' in bracket:
                    bracket_min = 0
                    bracket_max = 6000
                elif ' or more' in bracket:
                    parts = bracket.split('$')[1].split(' ')[0].replace(',', '')
                    bracket_min = int(parts)
                    bracket_max = float('inf')
                else:
                    parts = bracket.split('$')
                    bracket_min = int(parts[1].split(' ')[0].replace(',', ''))
                    bracket_max = int(parts[2].replace(',', ''))
                
                # Calculate overlap
                overlap_start = max(bracket_min, low)
                overlap_end = min(bracket_max, high)
                
                if overlap_start < overlap_end:
                    # Proportion of original bracket that falls in normalized bracket
                    if bracket_max == float('inf'):
                        # For open-ended brackets, assume exponential decay
                        proportion = 0.5  # Rough estimate
                    else:
                        bracket_width = bracket_max - bracket_min
                        overlap_width = overlap_end - overlap_start
                        proportion = overlap_width / bracket_width
                    
                    count += individuals * proportion
            
            bracket_label = f"${low//1000}K-${high//1000 if high != float('inf') else ''}K+"
            if high == float('inf'):
                bracket_label = f"${low//1000}K+"
            
            results.append({
                'income_year': year,
                'bracket': bracket_label,
                'min': low,
                'max': high,
                'individuals': count
            })
    
    return pd.DataFrame(results)

# Load the data
print("Loading tax data...")
df = pd.read_csv('ato_individual_tax_stats_by_demographics_2010_2023.csv')

# Focus on relevant years
years = ['2015–16', '2016–17', '2017–18']
df_years = df[df['income_year'].isin(years)]

# Aggregate by income bracket
print("\nAggregating by income bracket...")
agg_data = df_years.groupby(['income_year', 'taxable_income_range'])['individuals_count'].sum().reset_index()

# Analyze specific brackets around the $37K and $80-87K thresholds
print("\n=== Analysis of 2016-17 Tax Bracket Change ===")
print("\nContext: In 2016-17, the upper threshold for the 32.5% tax bracket")
print("was increased from $80,000 to $87,000.")

# Look at brackets around $37K (lower 32.5% threshold)
print("\n--- Brackets around $37K threshold ---")
for year in years:
    year_data = agg_data[agg_data['income_year'] == year]
    relevant_brackets = year_data[year_data['taxable_income_range'].str.contains('30,001|37,001|40,001|41,001|45,001')]
    print(f"\n{year}:")
    for _, row in relevant_brackets.iterrows():
        print(f"  {row['taxable_income_range']}: {row['individuals_count']:,.0f}")

# Look at brackets around $80-87K (upper 32.5% threshold change)
print("\n--- Brackets around $80-87K threshold ---")
for year in years:
    year_data = agg_data[agg_data['income_year'] == year]
    relevant_brackets = year_data[year_data['taxable_income_range'].str.contains('70,001|75,001|80,001|85,001|87,001|90,001')]
    print(f"\n{year}:")
    for _, row in relevant_brackets.iterrows():
        print(f"  {row['taxable_income_range']}: {row['individuals_count']:,.0f}")

# Normalize to 10K brackets for better comparison
print("\n--- Normalized to $10K brackets ---")
normalized_df = normalize_to_10k_brackets(agg_data)

# Show changes in key brackets
key_brackets = ['$30K-$40K', '$40K-$50K', '$70K-$80K', '$80K-$90K', '$90K-$100K']
for bracket in key_brackets:
    print(f"\n{bracket}:")
    for year in years:
        count = normalized_df[(normalized_df['income_year'] == year) & 
                             (normalized_df['bracket'] == bracket)]['individuals'].sum()
        print(f"  {year}: {count:,.0f}")
    
    if '2015–16' in years and '2016–17' in years:
        count_2015 = normalized_df[(normalized_df['income_year'] == '2015–16') & 
                                   (normalized_df['bracket'] == bracket)]['individuals'].sum()
        count_2016 = normalized_df[(normalized_df['income_year'] == '2016–17') & 
                                   (normalized_df['bracket'] == bracket)]['individuals'].sum()
        change = count_2016 - count_2015
        pct_change = (change / count_2015 * 100) if count_2015 > 0 else 0
        print(f"  Change 2015-16 to 2016-17: {change:,.0f} ({pct_change:+.1f}%)")

print("\n=== Key Findings ===")
print("1. The $37K threshold bracket expanded from $37-40K to $37-41K in 2016-17")
print("2. This captured more people in the bracket as incomes grew")
print("3. The upper threshold change from $80K to $87K would have reduced")
print("   tax for people earning between $80-87K (from 37% to 32.5% marginal rate)")