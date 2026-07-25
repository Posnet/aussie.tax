#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pandas",
#     "openpyxl"
# ]
# ///
"""
Extract the ATO "Individuals - Table 3" workbook into the two CSVs the rest of
the pipeline consumes.

Table 3B is the multi-year sheet (2010-11 onwards); Table 3A is the latest year
only and is ignored. The workbook's own sort prefixes ('aa.', 'a.') are rewritten
into the sortable forms used by this repo ('A00006000.', '00.') so that the
prefix encodes the bracket's bound rather than an opaque letter pair.

Outputs:
  data/ato_individual_tax_stats_by_demographics_2010_<end>.csv  all 52 columns
  data/ato_tax_stats_aggregates_2010_<end>.csv                  the 'all ranges' rows
  ato_2010-<end>.csv                                            9 columns, 15 brackets
"""

import argparse
import re
import sys

import pandas as pd

SHEET = 'Table 3B'
HEADER_ROW = 1  # row 1 is the workbook title, row 2 is the header

# Table 3B's 52 columns, in order. The workbook headers carry embedded newlines,
# footnote markers and trailing spaces, so map positionally rather than by name.
COLUMNS = [
    'income_year', 'sex', 'taxable_status', 'age_range', 'taxable_income_range',
    'tax_bracket', 'tax_bracket_range',
    'individuals_count',
    'salary_wages_count', 'salary_wages_amount',
    'total_income_count', 'total_income_amount',
    'car_expenses_count', 'car_expenses_amount',
    'travel_expenses_count', 'travel_expenses_amount',
    'uniform_expenses_count', 'uniform_expenses_amount',
    'education_expenses_count', 'education_expenses_amount',
    'other_work_expenses_count', 'other_work_expenses_amount',
    'donations_count', 'donations_amount',
    'tax_affairs_count', 'tax_affairs_amount',
    'ato_interest_count', 'ato_interest_amount',
    'litigation_count', 'litigation_amount',
    'other_tax_affairs_count', 'other_tax_affairs_amount',
    'total_deductions_count', 'total_deductions_amount',
    'capital_gains_count', 'capital_gains_amount',
    'rent_profit_count', 'rent_profit_amount',
    'rent_loss_count', 'rent_loss_amount',
    'net_rent_count', 'net_rent_amount',
    'business_income_count', 'business_income_amount',
    'business_expenses_count', 'business_expenses_amount',
    'net_business_count', 'net_business_amount',
    'taxable_income_count', 'taxable_income_amount',
    'net_tax_count', 'net_tax_amount',
]

# The 15 chart brackets, as (lower_bound, label). A raw ATO range is assigned to
# the bracket containing its lower bound — see normalize_income_range().
CHART_BRACKETS = [
    (0, '$6,000 or less'),
    (6001, '$6,001 to $10,000'),
    (10001, '$10,001 to $20,000'),
    (20001, '$20,001 to $30,000'),
    (30001, '$30,001 to $40,000'),
    (40001, '$40,001 to $50,000'),
    (50001, '$50,001 to $60,000'),
    (60001, '$60,001 to $80,000'),
    (80001, '$80,001 to $100,000'),
    (100001, '$100,001 to $150,000'),
    (150001, '$150,001 to $200,000'),
    (200001, '$200,001 to $250,000'),
    (250001, '$250,001 to $500,000'),
    (500001, '$500,001 to $1,000,000'),
    (1000001, '$1,000,001 or more'),
]

AGGREGATE_AGE = '99. all ranges'
AGGREGATE_INCOME = 'Z99. all ranges'


def strip_prefix(value):
    """'aa. $6,000 or less' -> '$6,000 or less'."""
    text = str(value)
    return text.split('. ', 1)[1] if '. ' in text else text


def parse_dollars(text):
    """Leading dollar figure of a bracket label, as an int."""
    match = re.search(r'\$([\d,]+)', text)
    if not match:
        raise ValueError(f'no dollar amount in {text!r}')
    return int(match.group(1).replace(',', ''))


def income_range_prefix(label):
    """Rebuild this repo's sortable income-range prefix.

    'A' for the open-ended bottom bracket (keyed on its upper bound), 'Y' for
    open-ended top brackets, 'B' for everything closed — all keyed on the bound
    that makes lexical order match numeric order.
    """
    if label == 'all ranges':
        return AGGREGATE_INCOME
    amount = parse_dollars(label)
    if label.endswith('or less'):
        return f'A{amount:08d}. {label}'
    if label.endswith('or more'):
        return f'Y{amount:08d}. {label}'
    return f'B{amount:08d}. {label}'


def age_range_prefix(label, index):
    """'Under 18' -> '00. Under 18'; the aggregate row keeps its 99. sentinel."""
    if label == 'all ranges':
        return AGGREGATE_AGE
    return f'{index:02d}. {label}'


def normalize_income_range(prefixed_label):
    """Collapse a raw ATO range into one of the 15 chart brackets.

    A range is assigned to the bracket holding its *upper* bound, which is what
    keeps the ATO's shifting cut-points lining up with the fixed chart brackets:
    the tax-reform-driven '$180,001 to $250,000' belongs with '$200,001 to
    $250,000', not with '$150,001 to $200,000'.

    Ranges that straddle a chart boundary ('$18,201 to $25,000',
    '$37,001 to $41,000') land wholly in the upper bracket. Open-ended ranges
    have no upper bound and fall back to their lower one, so the residual
    '$250,001 or more' bucket (14-52 people a year) joins '$250,001 to $500,000'.
    """
    label = strip_prefix(prefixed_label)
    if label.endswith('or more'):
        bound = parse_dollars(label)
    else:
        # '$6,000 or less' has a single figure, which is already its upper bound.
        bound = int(re.findall(r'\$([\d,]+)', label)[-1].replace(',', ''))

    chosen = CHART_BRACKETS[0][1]
    for lower, bracket in CHART_BRACKETS:
        if bound >= lower:
            chosen = bracket
        else:
            break
    return chosen


def load_table_3b(xlsx_path):
    """Read Table 3B and apply this repo's column names and sort prefixes."""
    df = pd.read_excel(xlsx_path, sheet_name=SHEET, header=HEADER_ROW)
    if df.shape[1] != len(COLUMNS):
        raise ValueError(
            f'{SHEET} has {df.shape[1]} columns, expected {len(COLUMNS)}. '
            'The ATO changed the table layout; update COLUMNS.')
    df.columns = COLUMNS

    # Every measure column arrives as text, with 'na' marking a figure the ATO
    # suppressed for privacy. Those become empty cells, as in the earlier data.
    for column in COLUMNS[7:]:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    # Age ranges are already alphabetically ordered by the workbook's prefix, so
    # the ordinal we need is just their rank.
    age_labels = sorted(df['age_range'].dropna().unique())
    age_index = {label: i for i, label in enumerate(age_labels)}
    df['age_range'] = df['age_range'].map(
        lambda v: age_range_prefix(strip_prefix(v), age_index[v]))
    df['taxable_income_range'] = df['taxable_income_range'].map(
        lambda v: income_range_prefix(strip_prefix(v)))
    return df


def split_aggregates(df):
    """Separate the 'all ranges' summary rows from the demographic detail."""
    is_aggregate = (
        (df['age_range'] == AGGREGATE_AGE)
        | (df['taxable_income_range'] == AGGREGATE_INCOME)
        | (df['sex'] == 'All')
        | (df['taxable_status'] == 'All')
    )
    return df[~is_aggregate].copy(), df[is_aggregate].copy()


def normalize(detail):
    """Aggregate the raw detail into the 9-column, 15-bracket chart dataset."""
    out = pd.DataFrame({
        # The ATO writes most years with an en dash but some with a hyphen;
        # the chart keys on the year string, so settle on the en dash here.
        'income_year': detail['income_year'].str.replace('-', '–', regex=False),
        'normalized_income_range': detail['taxable_income_range'].map(normalize_income_range),
        'sex': detail['sex'],
        'taxable_status': detail['taxable_status'],
        'age_range_display': detail['age_range'].map(strip_prefix),
        # Kept only for sorting: 'Under 18' has to lead, which it does not do
        # alphabetically.
        '_age': detail['age_range'].str.split('.').str[0].astype(int),
        'individuals_count': detail['individuals_count'],
        'total_income_amount': detail['total_income_amount'],
        'net_tax_amount': detail['net_tax_amount'],
    })
    out['income_range_display'] = out['normalized_income_range']

    grouped = out.groupby(
        ['income_year', 'normalized_income_range', 'income_range_display',
         'sex', 'taxable_status', 'age_range_display', '_age'],
        as_index=False,
    )[['individuals_count', 'total_income_amount', 'net_tax_amount']].sum()

    bracket_order = {label: i for i, (_, label) in enumerate(CHART_BRACKETS)}
    grouped['_bracket'] = grouped['normalized_income_range'].map(bracket_order)
    grouped = grouped.sort_values(
        ['income_year', '_bracket', 'sex', 'taxable_status', '_age']
    ).drop(columns=['_bracket', '_age'])

    return grouped[['income_year', 'normalized_income_range', 'income_range_display',
                    'sex', 'taxable_status', 'age_range_display',
                    'individuals_count', 'total_income_amount', 'net_tax_amount']]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--xlsx',
        default='data/ts24individual03sextaxablestatusagerangetaxableincomerange.xlsx',
        help='ATO Individuals Table 3 workbook')
    parser.add_argument(
        '--end-year', default='2024',
        help='calendar year the final financial year ends in, used in filenames')
    parser.add_argument(
        '--out-dir', default='.', help='repository root to write into')
    args = parser.parse_args()

    print(f'Reading {args.xlsx} [{SHEET}]...')
    df = load_table_3b(args.xlsx)
    print(f'  {len(df):,} rows, years {df["income_year"].min()} to {df["income_year"].max()}')

    detail, aggregates = split_aggregates(df)
    print(f'  {len(detail):,} detail rows, {len(aggregates):,} aggregate rows')

    raw_path = (f'{args.out_dir}/data/ato_individual_tax_stats_by_demographics'
                f'_2010_{args.end_year}.csv')
    agg_path = f'{args.out_dir}/data/ato_tax_stats_aggregates_2010_{args.end_year}.csv'
    norm_path = f'{args.out_dir}/ato_2010-{args.end_year}.csv'

    detail.to_csv(raw_path, index=False)
    aggregates.to_csv(agg_path, index=False)
    print(f'✓ {raw_path}')
    print(f'✓ {agg_path}')

    normalized = normalize(detail)
    normalized.to_csv(norm_path, index=False)
    print(f'✓ {norm_path} ({len(normalized):,} rows)')

    totals = normalized.groupby('income_year').agg(
        individuals=('individuals_count', 'sum'),
        income=('total_income_amount', 'sum'),
        tax=('net_tax_amount', 'sum'))
    totals['effective_rate'] = totals['tax'] / totals['income'] * 100
    print('\nYearly totals:')
    print(totals.to_string(
        formatters={'individuals': '{:,.0f}'.format,
                    'income': '${:,.0f}'.format,
                    'tax': '${:,.0f}'.format,
                    'effective_rate': '{:.2f}%'.format}))

    return 0


if __name__ == '__main__':
    sys.exit(main())
