// dashboard.js – Handles mock data, KPI cards, tables, and Plotly charts

// Utility to create a KPI card element
function createKpiCard(title, value, iconClass) {
  const card = document.createElement('div');
  card.className = 'kpi-card';
  card.innerHTML = `
    <div class="d-flex align-items-center mb-2">
      <i class="${iconClass} fs-3 me-2" style="color: var(--primary-color);"></i>
      <span class="card-title">${title}</span>
    </div>
    <div class="card-value">${value}</div>
  `;
  return card;
}

// Mock data – replace with real API calls later
const mockDashboard = {
  totalTourists: 1245,
  activeTourists: 987,
  missingTourists: 12,
  totalAlerts: 56,
  sosAlerts: 8,
  totalIncidents: 23,
  highRiskZones: 5,
  safetyScore: 78,
};

const mockAlerts = [
  { id: 'A001', name: 'John Doe', type: 'SOS', time: '2026-06-28 14:32', status: 'Resolved' },
  { id: 'A002', name: 'Jane Smith', type: 'Fall', time: '2026-06-28 16:10', status: 'Pending' },
  { id: 'A003', name: 'Luis García', type: 'Lost', time: '2026-06-28 18:45', status: 'Investigating' },
];

const mockIncidents = [
  { id: 'I001', name: 'Alice Brown', description: 'Minor injury in zone 3', risk: 'Low', status: 'Closed' },
  { id: 'I002', name: 'Bob Lee', description: 'Vehicle accident', risk: 'High', status: 'Open' },
  { id: 'I003', name: 'Carlos Ruiz', description: 'Lost child', risk: 'Critical', status: 'Escalated' },
];

// Render KPI cards
function renderKpiCards() {
  const mappings = [
    { id: 'card-total-tourists', title: 'Total Registered Tourists', value: mockDashboard.totalTourists, icon: 'bi bi-person' },
    { id: 'card-active-tourists', title: 'Active Tourists', value: mockDashboard.activeTourists, icon: 'bi bi-person-check' },
    { id: 'card-missing-tourists', title: 'Missing Tourists', value: mockDashboard.missingTourists, icon: 'bi bi-person-x' },
    { id: 'card-total-alerts', title: 'Total Alerts', value: mockDashboard.totalAlerts, icon: 'bi bi-bell' },
    { id: 'card-sos-alerts', title: 'Emergency SOS Alerts', value: mockDashboard.sosAlerts, icon: 'bi bi-exclamation-triangle' },
    { id: 'card-total-incidents', title: 'Total Incidents', value: mockDashboard.totalIncidents, icon: 'bi bi-archive' },
    { id: 'card-high-risk-zones', title: 'High Risk Zones', value: mockDashboard.highRiskZones, icon: 'bi bi-geo-alt' },
    { id: 'card-safety-score', title: 'Average Safety Score', value: mockDashboard.safetyScore + '%', icon: 'bi bi-speedometer2' },
  ];

  mappings.forEach(m => {
    const container = document.getElementById(m.id);
    if (container) {
      container.appendChild(createKpiCard(m.title, m.value, m.icon));
    }
  });
}

// Populate tables
function populateTable(tableId, rows, columns) {
  const tbody = document.querySelector(`#${tableId} tbody`);
  tbody.innerHTML = '';
  rows.forEach(row => {
    const tr = document.createElement('tr');
    columns.forEach(col => {
      const td = document.createElement('td');
      td.textContent = row[col];
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
}

function renderTables() {
  populateTable('table-alerts', mockAlerts, ['id', 'name', 'type', 'time', 'status']);
  populateTable('table-incidents', mockIncidents, ['id', 'name', 'description', 'risk', 'status']);
}

// Plotly charts – use mock time‑series data
function renderCharts() {
  // 1. Monthly Tourist Registration (Line)
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const registrations = [80, 95, 110, 130, 150, 170, 190, 210, 230, 250, 270, 300];
  Plotly.newPlot('chart-registration', [{
    x: months,
    y: registrations,
    type: 'scatter',
    mode: 'lines+markers',
    line: {color: 'var(--primary-color)'}
  }], {margin: {t: 20, b: 40}});

  // 2. Alert Distribution (Pie)
  const alertTypes = ['SOS', 'Fall', 'Lost', 'Other'];
  const alertCounts = [8, 15, 20, 13];
  Plotly.newPlot('chart-alerts', [{
    values: alertCounts,
    labels: alertTypes,
    type: 'pie',
    marker: {colors: ['#EF4444', '#F59E0B', '#22C55E', '#2563EB']}
  }], {margin: {t: 20, b: 40}});

  // 3. Incident Trend (Bar)
  const incidentMonths = months.slice(0, 6);
  const incidents = [2, 3, 5, 4, 6, 8];
  Plotly.newPlot('chart-incidents', [{
    x: incidentMonths,
    y: incidents,
    type: 'bar',
    marker: {color: '#EF4444'}
  }], {margin: {t: 20, b: 40}});
}

// Initialisation – replace real fetch calls with mock data for now
function initDashboard() {
  renderKpiCards();
  renderTables();
  renderCharts();
}

document.addEventListener('DOMContentLoaded', initDashboard);
