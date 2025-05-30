let salesChart, ordersChart;

// Fetch Sales Data from Backend
async function fetchSalesData() {
    try {
        const response = await fetch('/api/sales-orders-data');
        if (!response.ok) throw new Error('Failed to fetch data');
        const data = await response.json();
        console.log('API Response:', data); // Debug log
        return data;
    } catch (error) {
        console.error('Error fetching sales data:', error);
        return null;
    }
}

// Update Charts Based on Time Period
function updateCharts(timePeriod) {
    fetchSalesData().then(data => {
        if (!data || data.error) {
            console.error('Error:', data?.error || 'No data available');
            return;
        }

        console.log('Updating charts with:', data); // Debug log

        // Dashboard updates
        document.getElementById('totalSales').innerText = `Php ${(data[timePeriod]?.sales || 0).toFixed(2)}`;
        document.getElementById('totalOrders').innerText = data[timePeriod]?.orders || 0;

        // Sales Chart
        const salesData = Array(6).fill(data[timePeriod]?.sales || 0);
        console.log('Sales Data for Chart:', salesData); // Debug log
        salesChart.data.datasets[0].data = salesData;
        salesChart.update();

        // Orders Chart
        const bestsellers = data.bestsellers || { labels: [], data: [] };
        console.log('Bestsellers Data for Chart:', bestsellers); // Debug log
        ordersChart.data.labels = bestsellers.labels;
        ordersChart.data.datasets[0].data = bestsellers.data;
        ordersChart.update();
    });
}

// Initialize Charts
function initializeCharts() {
    const ctxSales = document.getElementById('salesChart').getContext('2d');
    salesChart = new Chart(ctxSales, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], // Placeholder labels
            datasets: [{
                label: 'Sales (Php)',
                data: [],
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                fill: true
            }]
        },
        options: { responsive: true }
    });

    const ctxOrders = document.getElementById('ordersChart').getContext('2d');
    ordersChart = new Chart(ctxOrders, {
        type: 'bar',
        data: {
            labels: [], // Placeholder labels for bestsellers
            datasets: [{
                label: 'Orders',
                data: [],
                backgroundColor: 'rgba(153, 102, 255, 0.6)'
            }]
        },
        options: { responsive: true }
    });
s
    // Default to Weekly Data
    updateCharts('weekly');
}

// Time Period Dropdown Event Listener
document.getElementById('timePeriod').addEventListener('change', (event) => {
    const selectedPeriod = event.target.value;
    updateCharts(selectedPeriod);
});

// Initialize the Charts on Page Load
document.addEventListener('DOMContentLoaded', initializeCharts);
