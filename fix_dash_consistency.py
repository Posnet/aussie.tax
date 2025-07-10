#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "pandas"
# ]
# ///
"""
Fix dash inconsistency in ato_2010-2023.csv to use em-dashes consistently.
"""

import pandas as pd

def main():
    print("Loading ato_2010-2023.csv...")
    df = pd.read_csv('ato_2010-2023.csv')
    
    print("Original year format sample:")
    print(df['income_year'].unique())
    
    # Replace regular dashes with em-dashes in income_year column
    df['income_year'] = df['income_year'].str.replace('-', '–')
    
    print("\nFixed year format sample:")
    print(df['income_year'].unique())
    
    # Save the fixed file
    df.to_csv('ato_2010-2023.csv', index=False)
    
    print("\n✓ Fixed dash consistency in ato_2010-2023.csv")
    print("✓ All years now use em-dashes consistently")

if __name__ == '__main__':
    main()