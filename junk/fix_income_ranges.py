#!/usr/bin/env python3
"""
Fix income range values to ensure proper lexicographic ordering.
"""

import pandas as pd
import re

def fix_income_range(val):
    """Convert income ranges to ensure proper sorting."""
    if pd.isna(val):
        return val
    
    val = str(val).strip()
    
    # Special cases first
    if val == 'all ranges':
        return 'Z99. all ranges'
    
    # Extract numbers from the range
    # Handle "or less", "or more", and "to" ranges
    if 'or less' in val:
        # e.g., "$6,000 or less"
        match = re.search(r'\$?([\d,]+)', val)
        if match:
            num = int(match.group(1).replace(',', ''))
            # Pad to 8 digits for proper sorting
            return f'A{num:08d}. {val}'
    
    elif 'or more' in val:
        # e.g., "$1,000,001 or more" or "$250,001 or more"
        match = re.search(r'\$?([\d,]+)', val)
        if match:
            num = int(match.group(1).replace(',', ''))
            # Use 'Y' prefix for "or more" ranges so they sort after regular ranges
            return f'Y{num:08d}. {val}'
    
    else:
        # Regular range, e.g., "$10,001 to $15,000"
        match = re.search(r'\$?([\d,]+)\s*to\s*\$?([\d,]+)', val)
        if match:
            start_num = int(match.group(1).replace(',', ''))
            end_num = int(match.group(2).replace(',', ''))
            # Use 'B' prefix for regular ranges, sort by start value
            return f'B{start_num:08d}. {val}'
    
    # If no pattern matches, return as-is
    return val

def main():
    # Load the main dataset
    df = pd.read_csv('ato_individual_tax_stats_by_demographics_2010_2023.csv')
    
    print("=== Fixing income range values for proper sorting ===")
    
    # Show original unique ranges
    original_ranges = sorted(df['taxable_income_range'].dropna().unique())
    print(f"\nOriginal ranges count: {len(original_ranges)}")
    
    # Apply the fix
    df['taxable_income_range'] = df['taxable_income_range'].apply(fix_income_range)
    
    # Show fixed ranges
    fixed_ranges = sorted(df['taxable_income_range'].dropna().unique())
    print(f"\nFixed ranges (first 5):")
    for r in fixed_ranges[:5]:
        print(f"  {r}")
    print("  ...")
    print(f"Fixed ranges (last 5):")
    for r in fixed_ranges[-5:]:
        print(f"  {r}")
    
    # Save the updated file
    df.to_csv('ato_individual_tax_stats_by_demographics_2010_2023.csv', index=False)
    print("\n✓ Updated main CSV file")
    
    # Also fix the aggregate file if it exists
    try:
        agg_df = pd.read_csv('ato_tax_stats_aggregates_2010_2023.csv')
        agg_df['taxable_income_range'] = agg_df['taxable_income_range'].apply(fix_income_range)
        agg_df.to_csv('ato_tax_stats_aggregates_2010_2023.csv', index=False)
        print("✓ Updated aggregate CSV file")
    except FileNotFoundError:
        print("✓ Aggregate file not found, skipping")
    
    print("\n✓ Income ranges now sort properly:")
    print("  - 'or less' ranges (A prefix) sort first")
    print("  - Regular 'to' ranges (B prefix) sort by starting value")
    print("  - 'or more' ranges (Y prefix) sort at the end")
    print("  - 'all ranges' (Z prefix) sorts last")

if __name__ == '__main__':
    main()