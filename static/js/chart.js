// Emotion Distribution Chart
var ctx = document.getElementById('emotionChart').getContext('2d');
new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['Happy', 'Sad', 'Angry', 'Neutral', 'Excited'],  // Replace with actual data or fetch via AJAX
        datasets: [{
            data: [10, 20, 15, 25, 30],  // Replace with actual data or fetch via AJAX
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
        }]
    }
});

// Mood Trend Chart
var ctx2 = document.getElementById('trendChart').getContext('2d');
new Chart(ctx2, {
    type: 'line',
    data: {
        labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5'],  // Replace with actual data or fetch via AJAX
        datasets: [{
            label: 'Mood Score',
            data: [5, 7, 6, 8, 9],  // Replace with actual data or fetch via AJAX
            borderColor: '#36A2EB',
            backgroundColor: 'rgba(54, 162, 235, 0.1)',
            borderWidth: 2,
            fill: true
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                max: 10
            }
        }
    }
});