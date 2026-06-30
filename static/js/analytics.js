// analytics.js - renders the Analytics dashboard using mock data and Plotly
// This file is designed to be easily swapped for real API calls later.

// ---- Mock Data -----------------------------------------------------------
const mockStats = {
  totalRegistered: 1245,
  activeTourists: 842,
  totalAlerts: 67,
  totalIncidents: 23,
  highRiskZones: 5,
  avgSafetyScore: 78.4,
};

const mockRegistrations = {
  months: [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ],
  values: [80, 95, 110, 120, 130, 140, 150, 145, 135, 125, 115, 100],
};

const mockActivity = {
  months: mockRegistrations.months,
  values: [300, 350, 400, 420, 440, 460, 480, 470, 450, 430, 410, 390],
};

const mockAlertDist = {
  labels: ['SOS Alerts', 'Risk Zone Alerts', 'Missing Tourist Alerts', 'AI Anomaly Alerts'],
  values: [25, 20, 15, 7],
};

const mockIncidentTrend = {
  months: mockRegistrations.months,
  values: [5, 8, 6, 10, 12, 9, 11, 10, 8, 7, 6, 5],
};

const mockSafetyScoreDist = {
  // Generate a simple distribution for demo purposes
  scores: [
    55, 60, 62, 65, 68, 70, 72, 73, 75, 77, 78, 80, 82, 84, 85, 86, 88, 90, 92, 95,
  ],
};

const mockRiskZoneDist = {
  labels: ['Low Risk', 'Medium Risk', 'High Risk'],
  values: [70, 20, 10],
};

// ---- Helper Functions ----------------------------------------------------
function createCard(iconClass, title, value) {
  const col = document.createElement('div');
  col.className = 'col-md-4 col-lg-2';
  col.innerHTML = `
    <div class="card h-100 shadow-sm rounded">
      <div class="card-body d-flex flex-column align-items-center justify-content-center text-center">
        <i class="${iconClass} mb-2" style="font-size: 2rem; color: var(--primary-color);"></i>
        <h6 class="card-title mb-1">${title}</h6>
        <p class="card-text fs-4 fw-bold">${value}</p>
      </div>
    </div>`;
  return col;
}

function renderStatsCards() {
  const container = document.getElementById('statsCards');
  const cards = [
    { icon: 'bi bi-people', title: 'Total Registered', value: mockStats.totalRegistered },
    { icon: 'bi bi-person-check', title: 'Active Tourists', value: mockStats.activeTourists },
    { icon: 'bi bi-bell', title: 'Total Alerts', value: mockStats.totalAlerts },
    { icon: 'bi bi-exclamation-triangle', title: 'Total Incidents', value: mockStats.totalIncidents },
    { icon: 'bi bi-geo-alt', title: 'High Risk Zones', value: mockStats.highRiskZones },
    { icon: 'bi bi-star', title: 'Avg Safety Score', value: mockStats.avgSafetyScore },
  ];
  cards.forEach(c => container.appendChild(createCard(c.icon, c.title, c.value)));
}

function plotLineChart(containerId, x, y, title) {
  const trace = { x, y, mode: 'lines+markers', type: 'scatter', line: { shape: 'spline' } };
  const layout = { title, margin: { t: 40, b: 40, l: 40, r: 20 }, responsive: true };
  Plotly.newPlot(containerId, [trace], layout, { displayModeBar: false, responsive: true });
}

function plotBarChart(containerId, x, y, title) {
  const trace = { x, y, type: 'bar', marker: { color: 'var(--primary-color)' } };
  const layout = { title, margin: { t: 40, b: 40, l: 40, r: 20 }, responsive: true };
  Plotly.newPlot(containerId, [trace], layout, { displayModeBar: false, responsive: true });
}

function plotPieChart(containerId, labels, values, title) {
  const trace = { labels, values, type: 'pie', hoverinfo: 'label+percent', textinfo: 'value' };
  const layout = { title, margin: { t: 40, b: 40, l: 20, r: 20 } };
  Plotly.newPlot(containerId, [trace], layout, { displayModeBar: false, responsive: true });
}

function plotHistogram(containerId, data, title) {
  const trace = { x: data, type: 'histogram', marker: { color: 'var(--primary-color)' } };
  const layout = { title, margin: { t: 40, b: 40, l: 40, r: 20 }, bargap: 0.05 };
  Plotly.newPlot(containerId, [trace], layout, { displayModeBar: false, responsive: true });
}

// ---- Rendering ----------------------------------------------------------
function renderCharts() {
  // 1. Monthly Tourist Registrations (Line)
  plotLineChart('chart-registrations', mockRegistrations.months, mockRegistrations.values, 'Monthly Tourist Registrations');

  // 2. Tourist Activity by Month (Bar)
  plotBarChart('chart-activity', mockActivity.months, mockActivity.values, 'Tourist Activity by Month');

  // 3. Alert Distribution (Pie)
  plotPieChart('chart-alerts', mockAlertDist.labels, mockAlertDist.values, 'Alert Distribution');

  // 4. Incident Trend (Bar)
  plotBarChart('chart-incidents', mockIncidentTrend.months, mockIncidentTrend.values, 'Incident Trend');

  // 5. Safety Score Distribution (Histogram)
  plotHistogram('chart-safety-score', mockSafetyScoreDist.scores, 'Safety Score Distribution');

  // 6. Risk Zone Distribution (Pie)
  plotPieChart('chart-risk-zones', mockRiskZoneDist.labels, mockRiskZoneDist.values, 'Risk Zone Distribution');
}

// ---- Filter Handlers (stub – can be expanded) ---------------------------
function applyFilters() {
  // For now just log filter values – real implementation would re‑fetch / re‑filter data.
  const from = document.getElementById('dateFrom').value;
  const to = document.getElementById('dateTo').value;
  const month = document.getElementById('monthFilter').value;
  const risk = document.getElementById('riskLevelFilter').value;
  console.log('Filters:', { from, to, month, risk });
  // TODO: Refetch data from /api/analytics with query params.
}

function initFilters() {
  document.getElementById('dateFrom').addEventListener('change', applyFilters);
  document.getElementById('dateTo').addEventListener('change', applyFilters);
  document.getElementById('monthFilter').addEventListener('change', applyFilters);
  document.getElementById('riskLevelFilter').addEventListener('change', applyFilters);
}

// ---- Bootstrap variable sync (optional) ---------------------------------
function syncThemeVariables() {
  const root = document.documentElement;
  // Colors are defined in dashboard.css – we expose them for JS if needed.
  const style = getComputedStyle(root);
  // Example: use primary color in Plotly traces (already using CSS variable).
  // No extra work needed for this demo.
}

// ---- Initialize ----------------------------------------------------------
window.addEventListener('DOMContentLoaded', () => {
  renderStatsCards();
  renderCharts();
  initFilters();
  syncThemeVariables();
});
