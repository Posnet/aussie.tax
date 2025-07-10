#!/bin/bash

echo "financial_year,inflation_factor_to_2022_23"

# Get inflation factors for each financial year relative to 2022-23
for year in 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022; do
    next_year=$((year + 1))
    fy_start="${year}%2F$(echo $next_year | cut -c3-4)"
    
    factor=$(curl -s 'https://www.rba.gov.au/calculator/financialYearDecimal.html' \
      -X POST \
      -H 'Content-Type: application/x-www-form-urlencoded' \
      --data-raw "financialYearDollar=1&financialStartYear=$fy_start&financialEndYear=2022%2F23&calculatedFinancialYearDollarValue=&idFinancialYearCalc=" \
      | grep -A1 'calculatedFinancialYearDollarValue' | grep 'value=' | sed 's/.*value="\([^"]*\)".*/\1/')
    
    echo "${year}–$(echo $next_year | cut -c3-4),$factor"
    sleep 0.5
done

# Add 2022-23 (base year)
echo "2022–23,1.00"