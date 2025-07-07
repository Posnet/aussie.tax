#!/usr/bin/env python3
"""
Fix age range values to ensure proper lexicographic ordering.
"""

import pandas as pd

def fix_age_range(val):
    """Convert age ranges to ensure proper sorting."""
    if pd.isna(val):
        return val
    
    val = str(val).strip()
    
    # Map the problematic values to sortable versions
    mappings = {
        'Under 18': '00. Under 18',
        '18 - 24': '01. 18 - 24',
        '25 - 29': '02. 25 - 29',
        '30 - 34': '03. 30 - 34',
        '35 - 39': '04. 35 - 39',
        '40 - 44': '05. 40 - 44',
        '45 - 49': '06. 45 - 49',
        '50 - 54': '07. 50 - 54',
        '55 - 59': '08. 55 - 59',
        '60 - 64': '09. 60 - 64',
        '65 - 69': '10. 65 - 69',
        '70 - 74': '11. 70 - 74',
        '75 and over': '12. 75 and over',
        'all ranges': '99. all ranges'  # Keep this for the aggregate file
    }
    
    return mappings.get(val, val)

def main():
    # Load the main dataset
    df = pd.read_csv('ato_individual_tax_stats_by_demographics_2010_2023.csv')
    
    print("=== Fixing age range values for proper sorting ===")
    print(f"Original unique age ranges: {sorted(df['age_range'].unique())}")
    
    # Apply the fix
    df['age_range'] = df['age_range'].apply(fix_age_range)
    
    print(f"\nFixed age ranges: {sorted(df['age_range'].unique())}")
    
    # Save the updated file
    df.to_csv('ato_individual_tax_stats_by_demographics_2010_2023.csv', index=False)
    print("\n✓ Updated main CSV file")
    
    # Also fix the aggregate file if it exists
    try:
        agg_df = pd.read_csv('ato_tax_stats_aggregates_2010_2023.csv')
        agg_df['age_range'] = agg_df['age_range'].apply(fix_age_range)
        agg_df.to_csv('ato_tax_stats_aggregates_2010_2023.csv', index=False)
        print("✓ Updated aggregate CSV file")
    except FileNotFoundError:
        print("✓ Aggregate file not found, skipping")
    
    # Update the JSON data for pivot table
    print("\n✓ Now regenerating pivot table data...")

if __name__ == '__main__':
    main()