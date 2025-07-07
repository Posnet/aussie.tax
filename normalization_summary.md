# Data Normalization Summary

## What Was Normalized

### 1. Income Range Consolidation
Reduced from **38 unique income ranges** to **15 consistent ranges** across all years:

- **$6,000 or less**
- **$6,001 to $10,000**
- **$10,001 to $20,000** (merged $10-15k, $15-20k, $10-18.2k ranges)
- **$20,001 to $30,000** (merged $20-25k, $25-30k ranges)
- **$30,001 to $40,000** (merged $30-37k, $37-40k ranges)
- **$40,001 to $50,000** (merged all $40-50k variations)
- **$50,001 to $60,000** (merged $50-55k, $55-60k ranges)
- **$60,001 to $80,000** (merged $60-70k, $70-80k variations)
- **$80,001 to $100,000** (merged $80-90k, $90-100k variations)
- **$100,001 to $150,000** (merged all $100-150k variations)
- **$150,001 to $200,000** (merged $150-180k, $180-200k ranges)
- **$200,001 to $250,000**
- **$250,001 to $500,000**
- **$500,001 to $1,000,000**
- **$1,000,001 or more**

### 2. Under 18 High Earners
- Original: "$250,001 or more" (privacy-protected aggregation)
- Normalized to: "$250,001 to $500,000"
- Affected: 236 individuals across all years

### 3. Tax Bracket Changes Over Time
The normalization handles three distinct periods of tax brackets:
- **2010-11 to 2011-12**: Original bracket structure
- **2012-13 to 2015-16**: Transitional brackets
- **2016-17 to 2022-23**: More granular modern brackets

## Data Integrity
- **Original total individuals**: 182,408,629
- **Normalized total individuals**: 182,408,629
- **Difference**: 0 (perfect preservation)

## Benefits for Visualization
1. **Consistent X-axis** across all years
2. **Smooth animations** without bracket jumping
3. **Better comparisons** between years
4. **Cleaner, more readable** chart
5. **No data loss** - all individuals accounted for

## Trade-offs
- Some granularity lost in middle income ranges
- Tax bracket boundaries don't align perfectly with policy years
- But gains in visual clarity and consistency outweigh these minor accuracy losses