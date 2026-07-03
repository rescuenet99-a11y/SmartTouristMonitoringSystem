// reports.js - Handles Reports dashboard UI with mock data and placeholders for export

// -------------------- Mock Data --------------------
const mockData = {
  summary: {
    totalTouristReports: 124,
    totalIncidentReports: 58,
    totalAlertReports: 92,
    totalRiskZoneReports: 12
  },
  tourist: [
    { id: "T001", name: "John Doe", destination: "Paris", safetyScore: 85, status: "Active" },
    { id: "T002", name: "Jane Smith", destination: "Rome", safetyScore: 78, status: "Inactive" },
    { id: "T003", name: "Ahmed Khan", destination: "Bangkok", safetyScore: 92, status: "Active" },
    // ... more rows can be added
  ],
  alert: [
    { id: "A100", tourist: "John Doe", type: "SOS", severity: "High", date: "2026-06-20", status: "Resolved" },
    { id: "A101", tourist: "Jane Smith", type: "Risk Zone", severity: "Medium", date: "2026-06-21", status: "Pending" },
    // ...
  ],
  incident: [
    { id: "I500", tourist: "Ahmed Khan", description: "Fall near Eiffel Tower", risk: "High", status: "Investigating", date: "2026-06-18" },
    // ...
  ],
  riskzone: [
    { name: "Zone A", level: "High", count: 45 },
    { name: "Zone B", level: "Medium", count: 30 },
    { name: "Zone C", level: "Low", count: 15 }
  ]
};

// -------------------- UI Helpers --------------------
function createCard(icon, title, value) {
  const col = document.createElement('div');
  col.className = 'col-md-3 col-lg-2';
  col.innerHTML = `
    <div class="card h-100 shadow-sm rounded">
      <div class="card-body d-flex flex-column align-items-center justify-content-center text-center">
        <i class="${icon} mb-2" style="font-size:2rem; color: var(--primary-color);"></i>
        <h6 class="card-title mb-1">${title}</h6>
        <p class="card-text fs-4 fw-bold">${value}</p>
      </div>
    </div>`;
  return col;
}

function renderSummaryCards() {
  const container = document.getElementById('summaryCards');
  const s = mockData.summary;
  const cards = [
    { icon: 'bi bi-people', title: 'Total Tourist Reports', value: s.totalTouristReports },
    { icon: 'bi bi-exclamation-triangle', title: 'Total Incident Reports', value: s.totalIncidentReports },
    { icon: 'bi bi-bell', title: 'Total Alert Reports', value: s.totalAlertReports },
    { icon: 'bi bi-geo-alt', title: 'Total Risk Zone Reports', value: s.totalRiskZoneReports }
  ];
  cards.forEach(c => container.appendChild(createCard(c.icon, c.title, c.value)));
}

// -------------------- Table Rendering --------------------
let currentReport = 'tourist'; // default view
let currentPage = 1;
const rowsPerPage = 8;
let currentSort = { column: null, asc: true };

function getHeaders(reportType) {
  switch (reportType) {
    case 'tourist':
      return [{ key: 'id', label: 'Tourist ID' }, { key: 'name', label: 'Tourist Name' }, { key: 'destination', label: 'Destination' }, { key: 'safetyScore', label: 'Safety Score' }, { key: 'status', label: 'Current Status' }];
    case 'alert':
      return [{ key: 'id', label: 'Alert ID' }, { key: 'tourist', label: 'Tourist' }, { key: 'type', label: 'Alert Type' }, { key: 'severity', label: 'Severity' }, { key: 'date', label: 'Date' }, { key: 'status', label: 'Status' }];
    case 'incident':
      return [{ key: 'id', label: 'Incident ID' }, { key: 'tourist', label: 'Tourist' }, { key: 'description', label: 'Description' }, { key: 'risk', label: 'Risk Level' }, { key: 'status', label: 'Status' }, { key: 'date', label: 'Date' }];
    case 'riskzone':
      return [{ key: 'name', label: 'Zone Name' }, { key: 'level', label: 'Risk Level' }, { key: 'count', label: 'Tourist Count' }];
    default:
      return [];
  }
}

function getData(reportType) {
  return mockData[reportType] || [];
}

function renderTableHeader(headers) {
  const headerRow = document.getElementById('tableHeader');
  headerRow.innerHTML = '';
  headers.forEach(h => {
    const th = document.createElement('th');
    th.textContent = h.label;
    th.style.cursor = 'pointer';
    th.dataset.key = h.key;
    th.addEventListener('click', () => sortByColumn(h.key));
    headerRow.appendChild(th);
  });
}

function sortByColumn(col) {
  const data = getData(currentReport);
  if (currentSort.column === col) {
    currentSort.asc = !currentSort.asc;
  } else {
    currentSort.column = col;
    currentSort.asc = true;
  }
  data.sort((a, b) => {
    const aVal = a[col];
    const bVal = b[col];
    if (aVal < bVal) return currentSort.asc ? -1 : 1;
    if (aVal > bVal) return currentSort.asc ? 1 : -1;
    return 0;
  });
  renderTableBody();
}

function renderTableBody() {
  const tbody = document.getElementById('tableBody');
  tbody.innerHTML = '';
  const data = getData(currentReport);
  const start = (currentPage - 1) * rowsPerPage;
  const pageData = data.slice(start, start + rowsPerPage);
  pageData.forEach(row => {
    const tr = document.createElement('tr');
    const headers = getHeaders(currentReport);
    headers.forEach(h => {
      const td = document.createElement('td');
      td.textContent = row[h.key];
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  renderPagination(data.length);
}

function renderPagination(totalRows) {
  const totalPages = Math.ceil(totalRows / rowsPerPage);
  const ul = document.getElementById('pagination');
  ul.innerHTML = '';
  for (let i = 1; i <= totalPages; i++) {
    const li = document.createElement('li');
    li.className = i === currentPage ? 'page-item active' : 'page-item';
    const a = document.createElement('a');
    a.className = 'page-link';
    a.href = '#';
    a.textContent = i;
    a.addEventListener('click', (e) => { e.preventDefault(); currentPage = i; renderTableBody(); });
    li.appendChild(a);
    ul.appendChild(li);
  }
}

function applyFilters() {
  // In a real implementation you would filter mockData based on UI fields.
  // For this demo we simply log the chosen filters.
  const search = document.getElementById('searchBox').value.trim().toLowerCase();
  const date = document.getElementById('dateFilter').value;
  const risk = document.getElementById('riskLevelFilter').value;
  const type = document.getElementById('reportTypeFilter').value;
  console.log('Filters applied:', { search, date, risk, type });
  // Switch report type if changed
  if (type && type !== currentReport) {
    currentReport = type;
    currentPage = 1;
    renderTableHeader(getHeaders(currentReport));
    renderTableBody();
  }
}

// -------------------- Export Placeholders --------------------
function placeholderExport(action) {
  alert(`${action} feature is a placeholder. Connect to backend to enable actual export.`);
}

function initExportButtons() {
  document.getElementById('exportPdf').addEventListener('click', () => placeholderExport('PDF Export'));
  document.getElementById('exportExcel').addEventListener('click', () => placeholderExport('Excel Export'));
  document.getElementById('printReport').addEventListener('click', () => placeholderExport('Print'));
}

// -------------------- Initialization --------------------
window.addEventListener('DOMContentLoaded', () => {
  renderSummaryCards();
  renderTableHeader(getHeaders(currentReport));
  renderTableBody();
  // Filter listeners
  document.getElementById('searchBox').addEventListener('input', applyFilters);
  document.getElementById('dateFilter').addEventListener('change', applyFilters);
  document.getElementById('riskLevelFilter').addEventListener('change', applyFilters);
  document.getElementById('reportTypeFilter').addEventListener('change', applyFilters);
  initExportButtons();
});
