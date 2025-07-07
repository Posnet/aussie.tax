#!/usr/bin/env python3
"""
Embed chart data and D3.js visualization code into the HTML file.
"""

import json
import pandas as pd

def main():
    # Read the chart data
    with open('chart_data.json', 'r') as f:
        chart_data = json.load(f)
    
    # Read the HTML template
    with open('ato_tax_animated_chart.html', 'r') as f:
        html_content = f.read()
    
    # Create the chart JavaScript code
    chart_js = '''
    <script>
        // Embedded data
        const chartData = ''' + json.dumps(chart_data, indent=2) + ''';
        
        // Initialize the visualization
        document.addEventListener('DOMContentLoaded', function() {
            const data = chartData.data;
            const summary = chartData.summary;
            
            // Hide loading, show chart
            document.getElementById('loading').style.display = 'none';
            document.getElementById('chart').style.display = 'block';
            
            // Set up dimensions
            const margin = {top: 40, right: 120, bottom: 120, left: 120};
            const width = document.getElementById('chart').offsetWidth - margin.left - margin.right;
            const height = 600 - margin.top - margin.bottom;
            
            // Create SVG
            const svg = d3.select('#chart')
                .append('svg')
                .attr('width', width + margin.left + margin.right)
                .attr('height', height + margin.top + margin.bottom);
            
            const g = svg.append('g')
                .attr('transform', `translate(${margin.left},${margin.top})`);
            
            // Color scales for different groupings
            const colorScales = {
                taxable_status: d3.scaleOrdinal()
                    .domain(['Taxable', 'Non Taxable'])
                    .range(['#3498db', '#e74c3c']),
                sex: d3.scaleOrdinal()
                    .domain(['Female', 'Male'])
                    .range(['#9b59b6', '#f39c12']),
                age_range: d3.scaleOrdinal()
                    .domain(summary.age_ranges)
                    .range(d3.schemeCategory10)
            };
            
            // Scales
            const xScale = d3.scaleBand()
                .domain(summary.income_ranges)
                .range([0, width])
                .padding(0.1);
            
            const yScale = d3.scaleLinear()
                .range([height, 0]);
            
            // Axes
            const xAxis = g.append('g')
                .attr('transform', `translate(0,${height})`)
                .attr('class', 'axis x-axis');
            
            const yAxis = g.append('g')
                .attr('class', 'axis y-axis');
            
            // Axis labels
            svg.append('text')
                .attr('transform', 'rotate(-90)')
                .attr('y', margin.left / 3)
                .attr('x', -(height / 2) - margin.top)
                .style('text-anchor', 'middle')
                .attr('class', 'axis-title')
                .text('Number of Individuals');
            
            svg.append('text')
                .attr('y', height + margin.top + margin.bottom - 10)
                .attr('x', (width / 2) + margin.left)
                .style('text-anchor', 'middle')
                .attr('class', 'axis-title')
                .text('Taxable Income Range');
            
            // Tooltip
            const tooltip = d3.select('#tooltip');
            
            // Update function
            function updateChart(yearIndex) {
                const year = summary.years[yearIndex];
                const colorBy = document.getElementById('colorBy').value;
                const filterSex = document.getElementById('filterSex').value;
                const filterTaxable = document.getElementById('filterTaxable').value;
                
                // Filter data for current year
                let yearData = data.filter(d => d.income_year === year);
                
                // Apply filters
                if (filterSex !== 'all') {
                    yearData = yearData.filter(d => d.sex === filterSex);
                }
                if (filterTaxable !== 'all') {
                    yearData = yearData.filter(d => d.taxable_status === filterTaxable);
                }
                
                // Group data by income range and color category
                const grouped = d3.rollup(yearData,
                    v => d3.sum(v, d => d.individuals_count),
                    d => d.taxable_income_range,
                    d => d[colorBy]
                );
                
                // Prepare stacked data
                const stackKeys = colorBy === 'taxable_status' ? ['Taxable', 'Non Taxable'] :
                                 colorBy === 'sex' ? ['Female', 'Male'] :
                                 summary.age_ranges;
                
                const stackedData = [];
                summary.income_ranges.forEach(incomeRange => {
                    const rangeData = {income_range: incomeRange};
                    let y0 = 0;
                    
                    stackKeys.forEach(key => {
                        const value = grouped.get(incomeRange)?.get(key) || 0;
                        rangeData[key] = {
                            y0: y0,
                            y1: y0 + value,
                            value: value,
                            key: key
                        };
                        y0 += value;
                    });
                    
                    rangeData.total = y0;
                    stackedData.push(rangeData);
                });
                
                // Update scales
                const maxY = d3.max(stackedData, d => d.total);
                yScale.domain([0, maxY * 1.1]);
                
                // Update axes with animation
                xAxis.transition()
                    .duration(750)
                    .call(d3.axisBottom(xScale)
                        .tickFormat((d, i) => summary.income_ranges_display[i]))
                    .selectAll('text')
                    .style('text-anchor', 'end')
                    .attr('dx', '-.8em')
                    .attr('dy', '.15em')
                    .attr('transform', 'rotate(-45)');
                
                yAxis.transition()
                    .duration(750)
                    .call(d3.axisLeft(yScale)
                        .tickFormat(d => d3.format('.2s')(d)));
                
                // Create bar groups
                const barGroups = g.selectAll('.bar-group')
                    .data(stackedData, d => d.income_range);
                
                const barGroupsEnter = barGroups.enter()
                    .append('g')
                    .attr('class', 'bar-group')
                    .attr('transform', d => `translate(${xScale(d.income_range)},0)`);
                
                // Update bar groups position
                barGroups.merge(barGroupsEnter)
                    .transition()
                    .duration(750)
                    .attr('transform', d => `translate(${xScale(d.income_range)},0)`);
                
                // Create/update bars for each stack
                stackKeys.forEach(key => {
                    const bars = g.selectAll('.bar-group')
                        .selectAll(`.bar-${key.replace(/[^a-zA-Z0-9]/g, '_')}`)
                        .data(d => [d[key]], d => d.key);
                    
                    bars.enter()
                        .append('rect')
                        .attr('class', `bar bar-${key.replace(/[^a-zA-Z0-9]/g, '_')}`)
                        .attr('width', xScale.bandwidth())
                        .attr('y', height)
                        .attr('height', 0)
                        .attr('fill', colorScales[colorBy](key))
                        .on('mouseover', function(event, d) {
                            const parentData = d3.select(this.parentNode).datum();
                            const incomeDisplay = summary.income_ranges_display[
                                summary.income_ranges.indexOf(parentData.income_range)
                            ];
                            
                            tooltip.html(`
                                <strong>${incomeDisplay}</strong><br>
                                ${key}: ${d3.format(',')(d.value)} individuals
                            `)
                            .style('left', (event.pageX + 10) + 'px')
                            .style('top', (event.pageY - 10) + 'px')
                            .style('opacity', 1);
                        })
                        .on('mouseout', function() {
                            tooltip.style('opacity', 0);
                        })
                        .merge(bars)
                        .transition()
                        .duration(750)
                        .attr('y', d => d.y0 ? yScale(d.y1) : height)
                        .attr('height', d => d.value > 0 ? yScale(d.y0) - yScale(d.y1) : 0)
                        .attr('fill', colorScales[colorBy](key));
                });
                
                // Update legend
                updateLegend(colorBy, stackKeys);
                
                // Update stats
                updateStats(yearData);
                
                // Update year display
                document.getElementById('yearDisplay').textContent = year;
            }
            
            function updateLegend(colorBy, keys) {
                const legend = d3.select('#legend');
                legend.selectAll('.legend-item').remove();
                
                keys.forEach(key => {
                    const item = legend.append('div')
                        .attr('class', 'legend-item');
                    
                    item.append('div')
                        .attr('class', 'legend-color')
                        .style('background-color', colorScales[colorBy](key));
                    
                    item.append('div')
                        .text(colorBy === 'age_range' ? 
                            summary.age_ranges_display[summary.age_ranges.indexOf(key)] : 
                            key);
                });
            }
            
            function updateStats(yearData) {
                const totalIndividuals = d3.sum(yearData, d => d.individuals_count);
                const totalIncome = d3.sum(yearData, d => d.total_income_amount);
                const totalTax = d3.sum(yearData, d => d.net_tax_amount);
                const effectiveRate = totalIncome > 0 ? (totalTax / totalIncome) * 100 : 0;
                
                document.getElementById('totalIndividuals').textContent = 
                    d3.format('.3s')(totalIndividuals);
                document.getElementById('totalIncome').textContent = 
                    '$' + d3.format('.3s')(totalIncome);
                document.getElementById('totalTax').textContent = 
                    '$' + d3.format('.3s')(totalTax);
                document.getElementById('effectiveRate').textContent = 
                    d3.format('.1f')(effectiveRate) + '%';
            }
            
            // Event listeners
            const yearSlider = document.getElementById('yearSlider');
            const playButton = document.getElementById('playButton');
            
            yearSlider.addEventListener('input', function() {
                updateChart(parseInt(this.value));
            });
            
            document.getElementById('colorBy').addEventListener('change', function() {
                updateChart(parseInt(yearSlider.value));
            });
            
            document.getElementById('filterSex').addEventListener('change', function() {
                updateChart(parseInt(yearSlider.value));
            });
            
            document.getElementById('filterTaxable').addEventListener('change', function() {
                updateChart(parseInt(yearSlider.value));
            });
            
            playButton.addEventListener('click', function() {
                if (isPlaying) {
                    clearInterval(playInterval);
                    isPlaying = false;
                    this.textContent = '▶ Play';
                    this.classList.remove('playing');
                } else {
                    isPlaying = true;
                    this.textContent = '⏸ Pause';
                    this.classList.add('playing');
                    
                    playInterval = setInterval(() => {
                        let currentValue = parseInt(yearSlider.value);
                        currentValue = (currentValue + 1) % summary.years.length;
                        yearSlider.value = currentValue;
                        updateChart(currentValue);
                        
                        if (currentValue === summary.years.length - 1) {
                            clearInterval(playInterval);
                            isPlaying = false;
                            playButton.textContent = '▶ Play';
                            playButton.classList.remove('playing');
                        }
                    }, 1500);
                }
            });
            
            // Initial chart
            updateChart(0);
        });
    </script>
'''
    
    # Insert the script before the closing body tag
    updated_html = html_content.replace('</body>', chart_js + '\n</body>')
    
    # Write the final self-contained HTML
    with open('ato_tax_animated_chart_standalone.html', 'w') as f:
        f.write(updated_html)
    
    print("✓ Created self-contained animated chart: ato_tax_animated_chart_standalone.html")
    print("✓ Features:")
    print("  - Stacked bar chart with income ranges on X-axis")
    print("  - Animated transitions between years (2010-11 to 2022-23)")
    print("  - Color by: Taxable Status, Gender, or Age Group")
    print("  - Filters for Gender and Taxable Status")
    print("  - Play button for automatic year progression")
    print("  - Interactive tooltips and real-time statistics")

if __name__ == '__main__':
    main()