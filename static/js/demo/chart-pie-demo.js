// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Pie Chart Example
(function() {
  var pieCtx = document.getElementById("myPieChart");

  function renderPieChart(labels, values) {
    return new Chart(pieCtx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc'],
        hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf'],
        hoverBorderColor: "rgba(234, 236, 244, 1)",
      }],
    },
    options: {
    maintainAspectRatio: false,
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
    },
    legend: {
      display: false
    },
    cutoutPercentage: 80,
    },
    });
  }

  if (pieCtx) {
    fetch('/api/chart-data')
      .then(resp => resp.json())
      .then(data => {
        var labels = (data && data.pie_chart && data.pie_chart.labels) || [];
        var values = (data && data.pie_chart && data.pie_chart.data) || [];
        renderPieChart(labels, values);
      })
      .catch(err => {
        renderPieChart(["Direct", "Referral", "Social"], [55, 30, 15]);
      });
  }
})();
