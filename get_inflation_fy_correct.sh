#!/bin/bash
# Scrape the RBA's financial-year inflation calculator for the factor that
# converts each historical financial year into base-year dollars.
#
#   ./get_inflation_fy_correct.sh > inflation_factors_fy_correct.csv

set -euo pipefail

BASE_START=2023          # base financial year is BASE_START/BASE_START+1
FIRST_YEAR=2010

base_fy="${BASE_START}/$(printf '%02d' $(( (BASE_START + 1) % 100 )))"
base_label="${BASE_START}–$(printf '%02d' $(( (BASE_START + 1) % 100 )))"

echo "financial_year,inflation_factor_to_${BASE_START}_$(printf '%02d' $(( (BASE_START + 1) % 100 ))),cpi_increase_percent"

for year in $(seq "$FIRST_YEAR" $((BASE_START - 1))); do
    fy="${year}/$(printf '%02d' $(( (year + 1) % 100 )))"

    factor=$(curl -s 'https://www.rba.gov.au/calculator/financialYearDecimal.html' \
      -X POST \
      -H 'Content-Type: application/x-www-form-urlencoded' \
      --data-urlencode "financialYearDollar=1" \
      --data-urlencode "financialStartYear=${fy}" \
      --data-urlencode "financialEndYear=${base_fy}" \
      --data-urlencode "calculatedFinancialYearDollarValue=" \
      --data-urlencode "idFinancialYearCalc=" \
      | grep -A2 'calculatedFinancialYearDollarValue' \
      | grep 'value=' \
      | sed 's/.*value="\([^"]*\)".*/\1/')

    if [ -z "$factor" ]; then
        echo "failed to read a factor for ${fy}" >&2
        exit 1
    fi

    increase=$(awk -v f="$factor" 'BEGIN { printf "%.1f", (f - 1) * 100 }')
    echo "${year}–$(printf '%02d' $(( (year + 1) % 100 ))),${factor},${increase}"
    sleep 0.5
done

# The base year is its own reference point.
echo "${base_label},1.00,0.0"
