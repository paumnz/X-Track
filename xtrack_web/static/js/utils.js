export async function getSessionData() {
    const response = await fetch('/get_session');
    const data = await response.json();
    return data
}

export function destroyChart(canvas_name) {
    var chart = Chart.getChart(canvas_name); // Get existing chart instance
    if (chart) {
        chart.destroy(); // Destroy the existing chart
    }
}

export function create_bar_plot(data, canvas_element) {
    var ctx = canvas_element.getContext('2d');
    ctx.clearRect(0, 0, canvas_element.width, canvas_element.height);
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data['labels'],
            datasets: [{
                data: data['data'],
                borderWidth: 1,
                backgroundColor: 'rgba(78, 204, 163, 0.5)',
                borderColor: 'rgba(78, 204, 163, 1)',
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                },
                x: {
                    ticks: {
                        autoSkip: false,
                        maxRotation: 90,
                        minRotation: 90
                    }
                },
            },
            plugins: {
                legend: {
                    display: false
                }
            },
        }
    });
}


export function create_line_plot(data, canvas_element, chart_label = 'Line Plot', x_label_ticks_shown = 1, legend_display = false) {
    var ctx = canvas_element.getContext('2d');
    ctx.clearRect(0, 0, canvas_element.width, canvas_element.height);

    if (data['x_values'].length === 0 || data['y_values'].length === 0) {
        // If data is empty, show a message on the canvas
        ctx.font = '16px Roboto, sans-serif';
        ctx.fillStyle = '#eaeaea';
        ctx.textAlign = 'center';
        ctx.fillText('No user creation dates were found.', canvas_element.width / 2, canvas_element.height / 2);
    } else {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data['x_values'],
                datasets: [{
                    label: chart_label,
                    data: data['y_values'],
                    fill: false,
                    borderColor: 'rgba(78, 204, 163, 1)',
                    backgroundColor: 'rgba(78, 204, 163, 0.5)',
                    tension: 0.1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    },
                    x: {
                        ticks: {
                            autoSkip: false,
                            maxRotation: 90,
                            minRotation: 90,
                            callback: function(value, index, ticks) {
                                return index % x_label_ticks_shown === 0 ? this.getLabelForValue(value) : '';
                            }
                        }
                    },
                },
                plugins: {
                    legend: {
                        display: legend_display
                    }
                }
            }
        });
    }
}


export function create_biline_plot(data, canvas_element, x1_col_name, y1_col_name, x2_col_name, y2_col_name, label_1 = 'Positive', label_2 = 'Negative', x_label_ticks_shown = 1, legend_display = false) {
    var ctx = canvas_element.getContext('2d');
    ctx.clearRect(0, 0, canvas_element.width, canvas_element.height);

    if (data[x1_col_name].length === 0 || data[y1_col_name].length === 0 || data[x2_col_name].length === 0 || data[y2_col_name].length === 0) {
        // If data is empty, show a message on the canvas
        ctx.font = '16px Roboto, sans-serif';
        ctx.fillStyle = '#eaeaea';
        ctx.textAlign = 'center';
        ctx.fillText('No data found for both sentiment line plots.', canvas_element.width / 2, canvas_element.height / 2);
    } else {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data[x1_col_name],
                datasets: [
                    {
                        label: label_1,
                        data: data[y1_col_name],
                        fill: false,
                        borderColor: 'rgba(78, 204, 163, 1)',
                        backgroundColor: 'rgba(78, 204, 163, 0.5)',
                        tension: 0.1
                    },
                    {
                        label: label_2,
                        data: data[y2_col_name],
                        fill: false,
                        borderColor: 'rgba(245, 34, 67, 1.0)',
                        backgroundColor: 'rgba(245, 34, 67, 0.5)',
                        tension: 0.1
                    },
                ]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    },
                    x: {
                        ticks: {
                            autoSkip: false,
                            maxRotation: 90,
                            minRotation: 90,
                            callback: function(value, index, ticks) {
                                return index % x_label_ticks_shown === 0 ? this.getLabelForValue(value) : '';
                            }
                        }
                    },
                },
                plugins: {
                    legend: {
                        display: legend_display
                    }
                }
            }
        });
    }
}


export function create_multiline_plot(data, canvas_element, x_label_ticks_shown = 1, legend_display = true) {
    var ctx = canvas_element.getContext('2d');
    ctx.clearRect(0, 0, canvas_element.width, canvas_element.height);

    const defaultColors = [
        'rgba(255, 99, 132, 1)',  // Red
        'rgba(54, 162, 235, 1)',  // Blue
        'rgba(75, 192, 192, 1)',  // Green
        'rgba(255, 206, 86, 1)',  // Yellow
        'rgba(153, 102, 255, 1)', // Purple
        'rgba(255, 159, 64, 1)',  // Orange
        'rgba(199, 199, 199, 1)', // Gray
        'rgba(83, 102, 255, 1)',  // Blueish
        'rgba(102, 205, 170, 1)', // Aquamarine
        'rgba(255, 69, 0, 1)'     // Red-Orange
    ];

    if (data['x_values'].length === 0 || data['y_values'].length === 0) {
        // If data is empty, show a message on the canvas
        ctx.font = '16px Roboto, sans-serif';
        ctx.fillStyle = '#eaeaea';
        ctx.textAlign = 'center';
        ctx.fillText('No data available for plotting.', canvas_element.width / 2, canvas_element.height / 2);
    } else {
        // Prepare datasets for each line
        const datasets = data['y_values'].map((y_values, index) => {
            const color = defaultColors[index % defaultColors.length];
            return {
                label: data.metrics[index],  // Label from the metrics array
                data: y_values,
                fill: false,
                borderColor: color,  // Varying color for each line
                backgroundColor: color.replace('1)', '0.5)'),
                tension: 0.1
            };
        });

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data['x_values'],
                datasets: datasets
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    },
                    x: {
                        ticks: {
                            autoSkip: false,
                            maxRotation: 90,
                            minRotation: 90,
                            callback: function(value, index, ticks) {
                                return index % x_label_ticks_shown === 0 ? this.getLabelForValue(value) : '';
                            }
                        }
                    },
                },
                plugins: {
                    legend: {
                        display: legend_display
                    }
                }
            }
        });
    }
}


export function create_plotly_figure(title, plotly_data, div_element_id, height = 800, hover_mode = true, layout = undefined) {
    if(!layout){
        layout = plotly_data.layout
    }
    
    const config = {
        responsive: true  // Ensure the chart resizes with the window or container
    };


    Plotly.newPlot(div_element_id, plotly_data.data, layout, config);
}


export function create_plotly_figure_subplots(title, plotly_data, div_element_id, height = 500, hover_mode = true) {
    const config = {
        responsive: true  // Ensure the chart resizes with the window or container
    };

    // Use the plotly_data.layout to ensure that subplots are properly configured
    Plotly.newPlot(div_element_id, plotly_data.data, plotly_data.layout, config);
}


export function create_pie_chart(data, canvas_element, chart_label = 'Pie Chart', min_percentage = 10) {
    var ctx = canvas_element.getContext('2d');
    ctx.clearRect(0, 0, canvas_element.width, canvas_element.height);

    if (data['labels'].length === 0 || data['values'].length === 0) {
        // If data is empty, show a message on the canvas
        ctx.font = '16px Roboto, sans-serif';
        ctx.fillStyle = '#eaeaea';
        ctx.textAlign = 'center';
        ctx.fillText('No data available.', canvas_element.width / 2, canvas_element.height / 2);
    } else {
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data['labels'],
                datasets: [{
                    label: chart_label,
                    data: data['values'],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        enabled: true,
                    },
                    datalabels: {
                        formatter: (value, context) => {
                            const total = context.dataset.data.reduce((acc, curr) => acc + curr, 0);
                            const percentage = (value / total) * 100;
                            // Only show percentage if it's greater than the specified minimum percentage
                            return percentage >= min_percentage ? `${percentage.toFixed(2)}%` : '';
                        },
                        color: '#FFFFFF', // Text color
                        font: {
                            weight: 'bold'
                        }
                    }
                }
            },
            plugins: [ChartDataLabels]
        });
    }
}

export function createTable(data, table_element) {

    // Clear any existing rows in the table body
    const tableBody = table_element.querySelector('tbody');
    tableBody.innerHTML = '';

    // Loop through the data and create rows
    data.forEach(rowData => {
        const row = document.createElement('tr');
        
        rowData.forEach(cellData => {
            const cell = document.createElement('td');
            cell.textContent = cellData;
            row.appendChild(cell);
        });

        // Append the row to the table body
        tableBody.appendChild(row);
    });
}


export function plotGraph(edges, sentimentDict, activityDict, div_element) {
    // Helper function to calculate color based on sentiment
    function getColor(sentiment) {
        const green = Math.round(255 * sentiment);
        const red = Math.round(255 * (1 - sentiment));
        return `rgb(${red}, ${green}, 0)`; // Generates a color from red to green
    }

    // Helper function to calculate size based on normalized activity
    function getSize(activity) {
        const minSize = 10;
        const maxSize = 50;
        // Scale activity between minSize and maxSize
        return minSize + activity * (maxSize - minSize);
    }

    // Extract unique nodes from the edges and apply sentiment colors and activity sizes
    var nodesSet = new Set();
    edges.forEach(edge => {
        nodesSet.add(edge.from);
        nodesSet.add(edge.to);
    });

    // Convert Set to an array of node objects with sentiment-based colors and activity-based sizes
    var nodes = Array.from(nodesSet).map(node => ({
        id: node,
        label: node,
        color: getColor(sentimentDict[node] || 0.5), // Default to neutral color if no sentiment value
        size: getSize(activityDict[node] || 0) // Default to smallest size if no activity value
    }));

    // Prepare the data for Vis.js
    var data = {
        nodes: new vis.DataSet(nodes),
        edges: new vis.DataSet(edges.map(edge => ({
            ...edge,
            label: edge.label || '',  // Ensure the edge label is present
            font: { align: 'middle' } // Align the label on the middle of the edge
        })))
    };

    // Set the visualization options
    var options = {
        edges: {
            arrows: 'to',
            labelHighlightBold: true,
            font: {
                size: 12,
                align: 'horizontal',
                color: '#343434', // Set color for the edge labels
                strokeWidth: 2, // Stroke around the label to make it more readable
                strokeColor: '#ffffff' // White stroke for better contrast
            },
            color: {
                color: '#848484',
                highlight: '#848484',
                hover: '#848484',
                opacity: 1.0,
            },
            width: 2,
            scaling: {
                min: 1,
                max: 10,
                label: true,
            },
            smooth: true,
        },
        nodes: {
            shape: 'dot',
            font: {
                size: 24,
                color: '#ffffff',
                face: 'arial', // Specify font face
            },
            borderWidth: 2,
            shadow: true
        },
        layout: {
            improvedLayout: true,
        },
        physics: {
            enabled: true,
            barnesHut: {
                gravitationalConstant: -2000,
                centralGravity: 0.5,
                springLength: 200,
                springConstant: 0.01,
                damping: 0.1,
                avoidOverlap: 0.1
            },
            maxVelocity: 10,
            minVelocity: 0.1,
            solver: 'barnesHut',
            stabilization: {
                enabled: true,
                iterations: 1000,
                updateInterval: 25,
                onlyDynamicEdges: false,
                fit: true
            },
            timestep: 0.5,
            adaptiveTimestep: true
        }
    };

    // Create the network graph
    new vis.Network(div_element, data, options);
}

