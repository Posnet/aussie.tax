#!/bin/bash

echo "year,inflation_factor_to_2023"

for year in {2010..2023}; do
    factor=$(curl -s 'https://www.rba.gov.au/calculator/annualDecimal.html' \
      -X POST \
      -H 'Content-Type: application/x-www-form-urlencoded' \
      --data-raw "annualDollar=1&annualStartYear=$year&annualEndYear=2023&calculatedAnnualDollarValue=&idACalc=" \
      | grep -A1 'calculatedAnnualDollarValue' | grep 'value=' | sed 's/.*value="\([^"]*\)".*/\1/')
    
    echo "$year,$factor"
    sleep 0.5  # Be polite to the server
done