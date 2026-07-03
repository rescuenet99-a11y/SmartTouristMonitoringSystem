/**
 * Trip Planner Module
 * Smart Tourist Monitoring System
 * 
 * This file handles dynamic form handling, validation, API integration, and dashboard state management.
 */

const API_BASE_URL = 'http://127.0.0.1:5000/api';

document.addEventListener('DOMContentLoaded', () => {
    // Form and input elements
    const tripForm = document.getElementById('trip-form');
    const destinationInput = document.getElementById('destination');
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const timeInput = document.getElementById('time');
    const transportSelect = document.getElementById('transport');
    const notesTextarea = document.getElementById('notes');
    const budgetInput = document.getElementById('budget');
    const validationAlert = document.getElementById('validation-alert');
    const startPlanningBtn = document.getElementById('start-planning-btn');
    const submitBtn = document.querySelector('.btn-submit');

    // Container elements
    const destinationContainer = document.getElementById('destination-container');
    const scheduleTbody = document.getElementById('schedule-tbody');
    const timelineContainer = document.getElementById('timeline-container');

    // Scroll to planning section on hero button click
    if (startPlanningBtn) {
        startPlanningBtn.addEventListener('click', () => {
            const planningSection = document.getElementById('planning-section');
            if (planningSection) {
                planningSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }

    // Initialize data from API
    loadTrips();

    // Handle Form Submission
    tripForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Do not reload the page

        // Extract form values
        const formData = {
            destination: destinationInput.value.trim(),
            startDate: startDateInput.value,
            endDate: endDateInput.value,
            time: timeInput.value,
            transport: transportSelect.value,
            notes: notesTextarea.value.trim(),
            budget: budgetInput.value ? parseFloat(budgetInput.value) : 0
        };

        // Validate fields
        const validationErrors = validateTripForm(formData);

        if (validationErrors.length > 0) {
            displayValidationErrors(validationErrors);
            return;
        }

        hideValidationError();

        // Show loading state
        const originalBtnText = submitBtn.textContent;
        submitBtn.textContent = 'Saving...';
        submitBtn.disabled = true;

        try {
            // Send data to backend API
            const response = await fetch(`${API_BASE_URL}/trips`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to save trip');
            }

            const savedTrip = await response.json();

            // Dynamically add components using the saved trip from backend
            addDestinationCard(savedTrip, savedTrip.id);
            addScheduleRow(savedTrip, savedTrip.id);
            addTimelineEvent(savedTrip, savedTrip.id);

            checkEmptyStates();
            tripForm.reset();

        } catch (error) {
            displayValidationErrors([error.message]);
        } finally {
            submitBtn.textContent = originalBtnText;
            submitBtn.disabled = false;
        }
    });

    /**
     * Load trips from the backend API
     */
    async function loadTrips() {
        try {
            const response = await fetch(`${API_BASE_URL}/trips`);
            if (!response.ok) throw new Error('Failed to fetch trips');
            
            const trips = await response.json();
            
            trips.forEach(trip => {
                addDestinationCard(trip, trip.id);
                addScheduleRow(trip, trip.id);
                addTimelineEvent(trip, trip.id);
            });
            
            checkEmptyStates();
        } catch (error) {
            console.error("Error loading trips:", error);
            displayValidationErrors(["Could not connect to backend server. Make sure the Flask server is running on port 5000."]);
        }
    }

    /**
     * Global delete function accessible from button onclick handlers
     * @param {number} id Unique trip identifier
     */
    window.deleteTrip = async function(id) {
        if (!confirm('Are you sure you want to delete this trip?')) return;
        
        try {
            const response = await fetch(`${API_BASE_URL}/trips/${id}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Failed to delete trip');

            // Remove from UI
            const card = document.getElementById(`card-${id}`);
            const row = document.getElementById(`row-${id}`);
            const timeline = document.getElementById(`timeline-${id}`);

            if (card) card.remove();
            if (row) row.remove();
            if (timeline) timeline.remove();

            checkEmptyStates();
        } catch (error) {
            alert(error.message);
        }
    };

    /**
     * Validate trip input fields
     */
    function validateTripForm(data) {
        const errors = [];

        if (!data.destination) errors.push('Destination name is required.');
        if (!data.startDate) errors.push('Start date is required.');
        if (!data.endDate) errors.push('End date is required.');
        
        if (data.startDate && data.endDate) {
            const start = new Date(data.startDate);
            const end = new Date(data.endDate);
            start.setHours(0,0,0,0);
            end.setHours(0,0,0,0);
            if (start > end) {
                errors.push('Start Date cannot be after End Date.');
            }
        }

        if (!data.time) errors.push('Travel time is required.');
        if (!data.transport) errors.push('Transport mode is required.');

        return errors;
    }

    function displayValidationErrors(errors) {
        validationAlert.innerHTML = ''; 
        const errorList = document.createElement('ul');
        errorList.style.paddingLeft = '1.25rem';
        errors.forEach(err => {
            const li = document.createElement('li');
            li.textContent = err;
            errorList.appendChild(li);
        });
        validationAlert.appendChild(errorList);
        validationAlert.style.display = 'block';
        validationAlert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function hideValidationError() {
        validationAlert.style.display = 'none';
        validationAlert.innerHTML = '';
    }

    function formatTime12Hour(timeString) {
        if (!timeString) return '';
        const [hoursStr, minutesStr] = timeString.split(':');
        let hours = parseInt(hoursStr, 10);
        const minutes = minutesStr;
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; 
        return `${hours}:${minutes} ${ampm}`;
    }

    function formatDateNice(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        const year = date.getUTCFullYear();
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const month = monthNames[date.getUTCMonth()];
        const day = date.getUTCDate();
        return `${day} ${month} ${year}`;
    }

    function getTripStatus(startDateStr, endDateStr) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const start = new Date(startDateStr);
        start.setHours(0, 0, 0, 0);
        const end = new Date(endDateStr);
        end.setHours(0, 0, 0, 0);

        if (today < start) return 'upcoming';
        else if (today > end) return 'completed';
        else return 'ongoing';
    }

    function addDestinationCard(data, id) {
        const card = document.createElement('div');
        card.className = 'destination-card';
        card.id = `card-${id}`;

        const transportIcon = getTransportIcon(data.transport);
        const dateRangeText = `${formatDateNice(data.startDate)} - ${formatDateNice(data.endDate)}`;
        const budgetHtml = data.budget > 0 ? `<p>💰 Budget: $${data.budget.toFixed(2)}</p>` : '';

        card.innerHTML = `
            <div class="destination-card-content">
                <h3>📍 ${escapeHtml(data.destination)}</h3>
                <p>📅 ${dateRangeText} | ${transportIcon} ${escapeHtml(data.transport)}</p>
                ${budgetHtml}
                ${data.notes ? `<p class="notes-preview">📝 ${escapeHtml(data.notes)}</p>` : ''}
            </div>
            <button class="btn-delete-card" title="Delete trip" onclick="deleteTrip(${id})">
                🗑️
            </button>
        `;
        destinationContainer.appendChild(card);
    }

    function addScheduleRow(data, id) {
        const row = document.createElement('tr');
        row.id = `row-${id}`;

        const status = getTripStatus(data.startDate, data.endDate);
        const formattedTime = formatTime12Hour(data.time);
        
        let badgeClass = 'badge-upcoming';
        if (status === 'ongoing') badgeClass = 'badge-ongoing';
        if (status === 'completed') badgeClass = 'badge-completed';

        row.innerHTML = `
            <td style="font-weight: 600;">📍 ${escapeHtml(data.destination)}</td>
            <td>${formatDateNice(data.startDate)}</td>
            <td>${formatDateNice(data.endDate)}</td>
            <td>${formattedTime}</td>
            <td>${escapeHtml(data.transport)}</td>
            <td>${data.budget > 0 ? '$' + data.budget.toFixed(2) : '-'}</td>
            <td><span class="badge ${badgeClass}">${status}</span></td>
            <td>
                <button class="btn-delete-row" onclick="deleteTrip(${id})">Delete</button>
            </td>
        `;
        scheduleTbody.appendChild(row);
    }

    function addTimelineEvent(data, id) {
        const timelineItem = document.createElement('div');
        timelineItem.className = 'timeline-item';
        timelineItem.id = `timeline-${id}`;

        const formattedTime = formatTime12Hour(data.time);
        const transportIcon = getTransportIcon(data.transport);
        const status = getTripStatus(data.startDate, data.endDate);

        timelineItem.innerHTML = `
            <div class="timeline-dot"></div>
            <div class="timeline-content">
                <div class="timeline-header">
                    <span class="timeline-title">📍 Heading to ${escapeHtml(data.destination)}</span>
                    <span class="timeline-date">${formatDateNice(data.startDate)}</span>
                </div>
                <div class="timeline-details">
                    <p><strong>Departure:</strong> ${formattedTime} via ${transportIcon} ${escapeHtml(data.transport)}</p>
                    <p><strong>Duration:</strong> ${formatDateNice(data.startDate)} to ${formatDateNice(data.endDate)} (${status})</p>
                    ${data.budget > 0 ? `<p><strong>Budget:</strong> $${data.budget.toFixed(2)}</p>` : ''}
                    ${data.notes ? `<div class="timeline-notes">"${escapeHtml(data.notes)}"</div>` : ''}
                </div>
            </div>
        `;
        insertTimelineChronologically(timelineItem, data.startDate);
    }

    function insertTimelineChronologically(newItem, newStartDateStr) {
        const items = timelineContainer.querySelectorAll('.timeline-item');
        const newDate = new Date(newStartDateStr);

        for (let i = 0; i < items.length; i++) {
            newItem.setAttribute('data-date', newStartDateStr);
            const existingDateStr = items[i].getAttribute('data-date');
            const existingDate = new Date(existingDateStr);

            if (newDate < existingDate) {
                timelineContainer.insertBefore(newItem, items[i]);
                return;
            }
        }
        newItem.setAttribute('data-date', newStartDateStr);
        timelineContainer.appendChild(newItem);
    }

    function getTransportIcon(mode) {
        if (mode.includes('Bus')) return '🚌';
        if (mode.includes('Train')) return '🚆';
        if (mode.includes('Flight')) return '✈️';
        if (mode.includes('Car')) return '🚗';
        return '🚗';
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function checkEmptyStates() {
        const destEmpty = document.getElementById('destination-empty');
        const destCards = destinationContainer.querySelectorAll('.destination-card');
        if (destEmpty) destEmpty.style.display = destCards.length === 0 ? 'block' : 'none';

        const scheduleEmpty = document.getElementById('schedule-empty');
        const scheduleRows = scheduleTbody.querySelectorAll('tr:not(#schedule-empty)');
        if (scheduleEmpty) scheduleEmpty.style.display = scheduleRows.length === 0 ? 'table-row' : 'none';

        const timelineEmpty = document.getElementById('timeline-empty');
        const timelineItems = timelineContainer.querySelectorAll('.timeline-item');
        if (timelineEmpty) timelineEmpty.style.display = timelineItems.length === 0 ? 'block' : 'none';
    }
});
