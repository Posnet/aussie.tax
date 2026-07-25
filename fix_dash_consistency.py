#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "pandas"
# ]
# ///
"""
Fix dash inconsistency in ato_2010-2024.csv to use em-dashes consistently.

Obsolete: extract_ato_source_data.py now normalises the ATO's mixed hyphen/en-dash
year labels on the way out, so this is a no-op on a freshly generated dataset.
Kept for re-fixing a hand-edited CSV.
"""

import pandas as pd

def main():
    print("Loading ato_2010-2024.csv...")
    df = pd.read_csv('ato_2010-2024.csv')
    
    print("Original year format sample:")
    print(df['income_year'].unique())
    
    # Replace regular dashes with em-dashes in income_year column
    df['income_year'] = df['income_year'].str.replace('-', '–')
    
    print("\nFixed year format sample:")
    print(df['income_year'].unique())
    
    # Save the fixed file
    df.to_csv('ato_2010-2024.csv', index=False)
    
    print("\n✓ Fixed dash consistency in ato_2010-2024.csv")
    print("✓ All years now use em-dashes consistently")

if __name__ == '__main__':
    main()