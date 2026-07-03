// script.js - Interactive behavior for Emergency Center page

// Update date and time every minute
function updateDateTime() {
  const dtElem = document.getElementById('datetime');
  if (!dtElem) return;
  const now = new Date();
  const options = {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  };
  dtElem.textContent = now.toLocaleString(undefined, options);
}

updateDateTime();
setInterval(updateDateTime, 60000);

// Placeholder click handlers for action buttons
const buttonIds = [
  'btn-sos',
  'btn-location',
  'btn-tracking',
  'btn-alerts',
  'btn-notifications',
  'btn-reports',
];
buttonIds.forEach((id) => {
  const btn = document.getElementById(id);
  if (btn) {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      alert(`${btn.textContent.trim()} feature coming soon.`);
    });
  }
});
