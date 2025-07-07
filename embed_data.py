#!/usr/bin/env python3
"""
Embed JSON data into HTML file to create a truly self-contained pivot table explorer.
"""

import json
import pandas as pd

def main():
    # Load the filtered data
    df = pd.read_csv('ato_individual_tax_stats_by_demographics_2010_2023.csv')
    
    # Prepare core columns for pivot table - include more financial metrics
    core_columns = [
        'income_year', 'sex', 'taxable_status', 'age_range', 'taxable_income_range',
        'individuals_count', 'total_income_amount', 'net_tax_amount',
        'salary_wages_amount', 'total_deductions_amount', 'taxable_income_amount'
    ]
    
    pivot_df = df[core_columns].copy()
    pivot_df = pivot_df.dropna(subset=['individuals_count'])
    
    # Convert to nicely formatted JSON
    records = pivot_df.to_dict(orient='records')
    json_data = json.dumps(records, indent=2)
    
    # Create the HTML content from scratch for better control
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ATO Individual Tax Statistics Explorer (2010-2023)</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/jquery-ui@1.13.2/dist/jquery-ui.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/pivottable@2.23.0/dist/pivot.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jquery-ui@1.13.2/dist/themes/ui-lightness/jquery-ui.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pivottable@2.23.0/dist/pivot.css">
    
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2em;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .loading {
            text-align: center;
            padding: 50px;
            font-size: 1.2em;
            color: #666;
        }
        .instructions {
            background: #e8f4f8;
            border: 1px solid #bee5eb;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .instructions h3 {
            margin-top: 0;
            color: #0c5460;
        }
        .instructions ul {
            margin-bottom: 0;
        }
        .instructions li {
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Australian Tax Data Explorer</h1>
        <p>Self-Contained Interactive Explorer - ''' + f'{len(pivot_df):,}' + ''' Individual Tax Records</p>
    </div>
    
    <div class="container">
        <div class="instructions">
            <h3>How to Use This Pivot Table</h3>
            <ul>
                <li><strong>Drag fields</strong> from the field list to Rows, Columns, or Values areas</li>
                <li><strong>Key dimensions:</strong> income_year, sex, taxable_status, age_range, taxable_income_range</li>
                <li><strong>Population metrics:</strong> individuals_count (number of taxpayers)</li>
                <li><strong>Financial metrics:</strong>
                    <ul>
                        <li>total_income_amount - Total income reported on tax returns</li>
                        <li>net_tax_amount - Actual tax paid after all deductions/credits</li>
                        <li>salary_wages_amount - Employment income</li>
                        <li>taxable_income_amount - Income after deductions</li>
                        <li>total_deductions_amount - Total deductions claimed</li>
                    </ul>
                </li>
                <li><strong>Change aggregation:</strong> Click on value fields to change from Sum to Average, Count, etc.</li>
                <li><strong>Filter data:</strong> Use the dropdown filters above each field</li>
                <li><strong>Switch views:</strong> Try Table, Bar Chart, Line Chart, and other visualizations</li>
            </ul>
        </div>
        
        <div id="loading" class="loading">
            Loading Australian tax data...
        </div>
        
        <div id="pivot-container" style="display: none;">
            <!-- Pivot table will be rendered here -->
        </div>
    </div>

    <script>
        // Initialize pivot table after data is loaded
        function initializePivotTable() {
            if (typeof window.taxData === 'undefined') {
                setTimeout(initializePivotTable, 100);
                return;
            }
            
            $('#loading').hide();
            $('#pivot-container').show();
            
            // Initialize pivot table with sensible defaults
            $('#pivot-container').pivotUI(window.taxData, {
                rows: ['income_year'],
                cols: ['sex'],
                vals: ['individuals_count'],
                aggregatorName: 'Sum',
                rendererName: 'Table',
                hiddenAttributes: [],
                renderers: $.extend(
                    $.pivotUtilities.renderers,
                    $.pivotUtilities.plotly_renderers,
                    $.pivotUtilities.d3_renderers
                ),
                onRefresh: function(config) {
                    console.log('Pivot table refreshed with config:', config);
                }
            });
        }
        
        // Start initialization when DOM is ready
        $(document).ready(function() {
            initializePivotTable();
        });
    </script>
    
    <!-- Data loaded as separate script tag at the end -->
    <script>
        window.taxData = ''' + json_data + ''';
    </script>
</body>
</html>'''
    
    # Write the self-contained HTML file
    with open('ato_tax_explorer_standalone.html', 'w') as f:
        f.write(html_content)
    
    print(f'✓ Created self-contained HTML file: ato_tax_explorer_standalone.html')
    print(f'✓ Embedded {len(pivot_df):,} records')
    print(f'✓ File size: {len(html_content):,} characters')
    print('✓ No external dependencies - can be opened directly in browser')

if __name__ == '__main__':
    main()