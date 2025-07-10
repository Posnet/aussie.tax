#!/bin/bash

echo "financial_year,start_year,inflation_factor_to_2023"

# For financial years, we'll use the end year (June) as the reference point
# e.g., for 2010-11, we'll use 2011
for start_year in {2010..2022}; do
    end_year=$((start_year + 1))
    fy="${start_year}-$(echo $end_year | cut -c3-4)"
    
    factor=$(curl -s 'https://www.rba.gov.au/calculator/annualDecimal.html' \
      -X POST \
      -H 'Content-Type: application/x-www-form-urlencoded' \
      --data-raw "annualDollar=1&annualStartYear=$end_year&annualEndYear=2023&calculatedAnnualDollarValue=&idACalc=" \
      | grep -A1 'calculatedAnnualDollarValue' | grep 'value=' | sed 's/.*value="\([^"]*\)".*/\1/')
    
    echo "${start_year}–$(echo $end_year | cut -c3-4),$end_year,$factor"
    sleep 0.5
done

# Add 2023-24 (which would use 2024, but we'll approximate with 2023)
echo "2023–24,2024,1.00"