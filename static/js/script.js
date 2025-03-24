document.addEventListener('DOMContentLoaded', () => {
    const scheduleDate = document.getElementById('schedule-date');
    if (scheduleDate) {
        scheduleDate.addEventListener('change', loadSchedule);
        loadSchedule(); // Initial load
    }

    const viewOnMap = document.getElementById('view-on-map');
    if (viewOnMap) {
        viewOnMap.addEventListener('click', (e) => {
            e.preventDefault();
            alert('Map view TBD');
        });
    }

    // Add event listener for the "Report Missing Event" button
    const reportMissingEvent = document.getElementById('report-missing-event');
    if (reportMissingEvent) {
        reportMissingEvent.addEventListener('click', () => showReportDialog(null, 'add-missing'));
    }
});

async function loadSchedule() {
    const path = window.location.pathname.split('/').filter(Boolean);
    const building = path[1];
    const floor = path[2];
    const room = path[3];
    const date = document.getElementById('schedule-date').value;
    const response = await fetch(`/api/schedule/${building}/${floor}/${room}`);
    const schedule = await response.json();
    const scheduleTable = document.getElementById('schedule');
    scheduleTable.innerHTML = '';

    if (!schedule[date] || schedule[date].length === 0) {
        scheduleTable.innerHTML = '<tr><td colspan="4">No events scheduled.</td></tr>';
    } else {
        schedule[date].forEach(slot => {
            const tr = document.createElement('tr');
            const time = `${slot.start_time} - ${slot.end_time}`;
            const isUserCreated = slot.is_user_created ? 'true' : 'false';
            tr.innerHTML = `
                <td>${time}</td>
                <td>${slot.status}</td>
                <td>${slot.event_title || ''}</td>
                <td><button class="report-change" data-time="${time}" data-status="${slot.status}" data-event="${slot.event_title || ''}" data-user-created="${isUserCreated}">Report Change</button></td>
            `;
            scheduleTable.appendChild(tr);
        });

        // Add event listeners for report buttons
        document.querySelectorAll('.report-change').forEach(button => {
            button.addEventListener('click', () => showReportDialog(button));
        });
    }
}

function showReportDialog(button, mode = 'report') {
    const dialog = document.getElementById('report-dialog');
    const dialogTitle = document.getElementById('dialog-title');
    const dialogMessage = document.getElementById('dialog-message');
    const dialogForm = document.getElementById('dialog-form');
    const eventTitleLabel = document.getElementById('event-title-label');
    const startTimeLabel = document.getElementById('start-time-label');
    const endTimeLabel = document.getElementById('end-time-label');
    const explanationLabel = document.getElementById('explanation-label');
    const confirmButton = document.getElementById('dialog-confirm');

    const path = window.location.pathname.split('/').filter(Boolean);
    const building = path[1];
    const floor = path[2];
    const room = path[3];

    // Reset visibility of form fields
    eventTitleLabel.style.display = 'none';
    startTimeLabel.style.display = 'none';
    endTimeLabel.style.display = 'none';
    explanationLabel.style.display = 'none';

    if (mode === 'add-missing') {
        // Case: Report a missing event
        dialogTitle.textContent = `Is there an event in ${building} ${floor}.${room} on ${document.getElementById('schedule-date').value}?`;
        dialogMessage.textContent = 'Let us know:';
        eventTitleLabel.style.display = 'block';
        startTimeLabel.style.display = 'block';
        endTimeLabel.style.display = 'block';
        confirmButton.textContent = 'Add Event';
        confirmButton.onclick = () => submitReport(building, floor, room, null, 'add');
    } else {
        // Existing cases for reporting changes
        const time = button.dataset.time;
        const status = button.dataset.status;
        const event = button.dataset.event;
        const isUserCreated = button.dataset.userCreated === 'true';

        if (status === 'Occupied' && event && !isUserCreated) {
            // System event exists
            dialogTitle.textContent = 'Is this event not happening?';
            dialogMessage.textContent = `Report as cancelled:`;
            eventTitleLabel.style.display = 'none';
            explanationLabel.style.display = 'block';
            confirmButton.textContent = 'Report Cancelled';
            confirmButton.onclick = () => submitReport(building, floor, room, time, 'cancelled');
        } else if (status === 'Available') {
            // Unoccupied slot (handled by "Report Missing Event" button now)
            dialogTitle.textContent = `Is there an event in ${building} ${floor}.${room} on ${document.getElementById('schedule-date').value}?`;
            dialogMessage.textContent = 'Let us know:';
            eventTitleLabel.style.display = 'block';
            startTimeLabel.style.display = 'block';
            endTimeLabel.style.display = 'block';
            confirmButton.textContent = 'Add Event';
            confirmButton.onclick = () => submitReport(building, floor, room, time, 'add');
        } else if (status === 'Occupied' && isUserCreated) {
            // User-created event
            dialogTitle.textContent = 'Is this user-reported event not happening?';
            dialogMessage.textContent = 'Confirm event removal:';
            eventTitleLabel.style.display = 'none';
            explanationLabel.style.display = 'none';
            confirmButton.textContent = 'Remove Event';
            confirmButton.onclick = () => submitReport(building, floor, room, time, 'remove');
        }
    }

    dialog.style.display = 'flex';

    document.getElementById('dialog-cancel').onclick = () => {
        dialog.style.display = 'none';
    };
}

async function submitReport(building, floor, room, time, reportType) {
    const eventTitle = document.getElementById('event-title')?.value || '';
    const startTime = document.getElementById('start-time')?.value || '';
    const endTime = document.getElementById('end-time')?.value || '';
    const explanation = document.getElementById('explanation')?.value || '';
    const date = document.getElementById('schedule-date').value;
    // For new events, construct the time block from start and end times
    const timeBlock = time || (startTime && endTime ? `${startTime} - ${endTime}` : '');
    const response = await fetch('/api/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `building=${building}&floor=${floor}&room=${room}&time_block=${timeBlock}&report_type=${reportType}&event_title=${eventTitle}&explanation=${explanation}&date=${date}`
    });
    const result = await response.json();
    alert(`Report status: ${result.status}`);
    document.getElementById('report-dialog').style.display = 'none';
    loadSchedule(); // Refresh schedule
}