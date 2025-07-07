#!/usr/bin/env python3
"""
Create a normalized dataset for chart visualization with consistent income ranges across all years.
"""

import pandas as pd
import numpy as np

def get_normalized_range(original_range):
    """Map original income ranges to normalized ranges."""
    if pd.isna(original_range):
        return original_range
    
    # Remove prefix for comparison
    clean_range = original_range
    if '. ' in str(original_range):
        clean_range = str(original_range).split('. ', 1)[1]
    
    # Mapping dictionary
    mapping = {
        # Low income ranges - keep as is
        '$6,000 or less': '$6,000 or less',
        '$6,001 to $10,000': '$6,001 to $10,000',
        
        # $10k-20k consolidation
        '$10,001 to $15,000': '$10,001 to $20,000',
        '$15,001 to $20,000': '$10,001 to $20,000',
        '$10,001 to $18,200': '$10,001 to $20,000',
        '$18,201 to $25,000': '$20,001 to $30,000',
        
        # $20k-30k consolidation
        '$20,001 to $25,000': '$20,001 to $30,000',
        '$25,001 to $30,000': '$20,001 to $30,000',
        
        # $30k-40k consolidation
        '$30,001 to $37,000': '$30,001 to $40,000',
        '$37,001 to $40,000': '$30,001 to $40,000',
        '$37,001 to $41,000': '$40,001 to $50,000',
        
        # $40k-50k consolidation
        '$40,001 to $45,000': '$40,001 to $50,000',
        '$41,001 to $45,000': '$40,001 to $50,000',
        '$45,001 to $50,000': '$40,001 to $50,000',
        '$45,001 to $48,000': '$40,001 to $50,000',
        '$48,001 to $50,000': '$40,001 to $50,000',
        
        # $50k-60k - keep as is
        '$50,001 to $55,000': '$50,001 to $60,000',
        '$55,001 to $60,000': '$50,001 to $60,000',
        
        # $60k-80k consolidation
        '$60,001 to $70,000': '$60,001 to $80,000',
        '$60,001 to $66,667': '$60,001 to $80,000',
        '$66,668 to $70,000': '$60,001 to $80,000',
        '$70,001 to $80,000': '$60,001 to $80,000',
        
        # $80k-100k consolidation
        '$80,001 to $90,000': '$80,001 to $100,000',
        '$80,001 to $87,000': '$80,001 to $100,000',
        '$87,001 to $90,000': '$80,001 to $100,000',
        '$90,001 to $100,000': '$80,001 to $100,000',
        
        # $100k-150k consolidation
        '$100,001 to $150,000': '$100,001 to $150,000',
        '$100,001 to $120,000': '$100,001 to $150,000',
        '$120,001 to $125,333': '$100,001 to $150,000',
        '$125,334 to $150,000': '$100,001 to $150,000',
        
        # $150k-200k consolidation
        '$150,001 to $180,000': '$150,001 to $200,000',
        '$180,001 to $250,000': '$200,001 to $250,000',
        '$180,001 to $200,000': '$150,001 to $200,000',
        '$200,001 to $250,000': '$200,001 to $250,000',
        
        # High income ranges - keep as is
        '$250,001 to $500,000': '$250,001 to $500,000',
        '$500,001 to $1,000,000': '$500,001 to $1,000,000',
        '$1,000,001 or more': '$1,000,001 or more',
        
        # Special case for under 18 high earners
        '$250,001 or more': '$250,001 to $500,000',  # Map to first high bracket
        
        # All ranges catch-all
        'all ranges': 'all ranges'
    }
    
    return mapping.get(clean_range, clean_range)

def main():
    # Load the data
    df = pd.read_csv('ato_individual_tax_stats_by_demographics_2010_2023.csv')
    
    print("=== Creating Normalized Dataset ===\n")
    
    # Create normalized income range column
    df['normalized_income_range'] = df['taxable_income_range'].apply(
        lambda x: get_normalized_range(x) if pd.notna(x) else x
    )
    
    # Define the order for normalized ranges
    normalized_order = [
        '$6,000 or less',
        '$6,001 to $10,000',
        '$10,001 to $20,000',
        '$20,001 to $30,000',
        '$30,001 to $40,000',
        '$40,001 to $50,000',
        '$50,001 to $60,000',
        '$60,001 to $80,000',
        '$80,001 to $100,000',
        '$100,001 to $150,000',
        '$150,001 to $200,000',
        '$200,001 to $250,000',
        '$250,001 to $500,000',
        '$500,001 to $1,000,000',
        '$1,000,001 or more'
    ]
    
    # Group by all dimensions except the original income range
    group_cols = ['income_year', 'sex', 'taxable_status', 'age_range', 'normalized_income_range']
    
    # Aggregate numeric columns
    agg_dict = {}
    numeric_cols = [col for col in df.columns if col.endswith('_count') or col.endswith('_amount')]
    for col in numeric_cols:
        agg_dict[col] = 'sum'
    
    # Group and aggregate
    normalized_df = df.groupby(group_cols).agg(agg_dict).reset_index()
    
    # Add display-friendly columns
    normalized_df['income_range_display'] = normalized_df['normalized_income_range']
    normalized_df['age_range_display'] = normalized_df['age_range'].apply(
        lambda x: x.split('. ', 1)[1] if pd.notna(x) and '. ' in str(x) else x
    )
    
    # Sort by year and normalized income range
    normalized_df['income_range_sort'] = normalized_df['normalized_income_range'].apply(
        lambda x: normalized_order.index(x) if x in normalized_order else 999
    )
    normalized_df = normalized_df.sort_values(['income_year', 'income_range_sort'])
    normalized_df = normalized_df.drop('income_range_sort', axis=1)
    
    # Save the normalized dataset
    output_file = 'ato_tax_data_normalized_for_chart.csv'
    normalized_df.to_csv(output_file, index=False)
    
    print(f"✓ Created normalized dataset: {output_file}")
    print(f"✓ Total records: {len(normalized_df):,}")
    print(f"✓ Normalized income ranges: {len(normalized_order)}")
    
    # Show before/after comparison
    print("\n=== Normalization Summary ===")
    original_ranges = df['taxable_income_range'].nunique()
    normalized_ranges = normalized_df['normalized_income_range'].nunique()
    print(f"Original unique income ranges: {original_ranges}")
    print(f"Normalized unique income ranges: {normalized_ranges}")
    
    # Check specific cases
    print("\n=== Under 18 High Earners Normalization ===")
    under18_original = df[
        (df['age_range'] == '00. Under 18') & 
        (df['taxable_income_range'].str.contains('250,001 or more', na=False))
    ]
    under18_normalized = normalized_df[
        (normalized_df['age_range'] == '00. Under 18') & 
        (normalized_df['normalized_income_range'] == '$250,001 to $500,000')
    ]
    
    print(f"Original '$250,001 or more' for Under 18: {len(under18_original)} rows")
    print(f"Normalized to '$250,001 to $500,000': {len(under18_normalized)} rows")
    print(f"Total individuals affected: {under18_normalized['individuals_count'].sum():.0f}")
    
    # Verify data integrity
    print("\n=== Data Integrity Check ===")
    original_total = df['individuals_count'].sum()
    normalized_total = normalized_df['individuals_count'].sum()
    print(f"Original total individuals: {original_total:,.0f}")
    print(f"Normalized total individuals: {normalized_total:,.0f}")
    print(f"Difference: {abs(original_total - normalized_total):,.0f} ({abs(original_total - normalized_total)/original_total*100:.2f}%)")

if __name__ == '__main__':
    main()