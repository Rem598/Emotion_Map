// Heatmap Chart Initialization
document.addEventListener('DOMContentLoaded', function() {
    // Get data from hidden script tag
    const heatmapDataElement = document.getElementById('heatmap-data');
    
    if (!heatmapDataElement) {
        console.error('Heatmap data not found');
        return;
    }
    
    let heatmapData;
    try {
        heatmapData = JSON.parse(heatmapDataElement.textContent);
    } catch (error) {
        console.error('Error parsing heatmap data:', error);
        return;
    }
    
    // Get canvas element
    const canvas = document.getElementById('heatmapChart');
    if (!canvas) {
        console.error('Canvas element not found');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    // Prepare scatter data for heatmap
    const scatterData = [];
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    
    heatmapData.forEach((dayObj, dayIndex) => {
        dayObj.data.forEach((intensity, hour) => {
            if (intensity > 0) {
                scatterData.push({
                    x: hour,
                    y: dayIndex,
                    v: intensity,
                    day: dayObj.day
                });
            }
        });
    });
    
    // Create the heatmap chart
    const chart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Mood Intensity',
                data: scatterData,
                backgroundColor: function(context) {
                    const value = context.raw.v;
                    if (!value || value === 0) {
                        return 'rgba(200, 200, 200, 0.1)';
                    }
                    // Create intensity-based color
                    const intensity = value / 10;
                    return `rgba(147, 51, 234, ${intensity})`;
                },
                borderColor: 'white',
                borderWidth: 2,
                pointRadius: 15,
                pointHoverRadius: 18
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        title: function(context) {
                            const point = context[0].raw;
                            return point.day + ' at ' + point.x + ':00';
                        },
                        label: function(context) {
                            const point = context.raw;
                            return 'Average Intensity: ' + point.v.toFixed(1) + '/10';
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    min: 0,
                    max: 23,
                    ticks: {
                        stepSize: 1,
                        font: {
                            size: 11
                        },
                        callback: function(value) {
                            // Show only every 3rd hour to avoid crowding
                            return value % 3 === 0 ? value + ':00' : '';
                        }
                    },
                    title: {
                        display: true,
                        text: 'Hour of Day',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y: {
                    type: 'linear',
                    min: -0.5,
                    max: 6.5,
                    ticks: {
                        stepSize: 1,
                        font: {
                            size: 12
                        },
                        callback: function(value) {
                            if (value >= 0 && value < days.length) {
                                return days[Math.round(value)];
                            }
                            return '';
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
    
    console.log('Heatmap chart initialized successfully with', scatterData.length, 'data points');
});