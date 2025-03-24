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
});

async function loadSchedule() {
    const path = window.location.pathname.split('/');
    const building = path[2];
    const floor = path[3];
    const room = path[4];
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
            tr.innerHTML = `
                <td>${time}</td>
                <td>${slot.status}</td>
                <td>${slot.event_title || ''}</td>
                <td><button class="report-change" data-time="${time}" data-status="${slot.status}" data-event="${slot.event_title || ''}">Report Change</button></td>
            `;
            scheduleTable.appendChild(tr);
        });

        // Add event listeners for report buttons
        document.querySelectorAll('.report-change').forEach(button => {
            button.addEventListener('click', () => showReportDialog(button));
        });
    }
}

function showReportDialog(button) {
    const dialog = document.getElementById('report-dialog');
    const dialogTitle = document.getElementById('dialog-title');
    const dialogMessage = document.getElementById('dialog-message');
    const dialogForm = document.getElementById('dialog-form');
    const eventTitleLabel = document.getElementById('event-title-label');
    const explanationLabel = document.getElementById('explanation-label');
    const confirmButton = document.getElementById('dialog-confirm');

    const time = button.dataset.time;
    const status = button.dataset.status;
    const event = button.dataset.event;
    const path = window.location.pathname.split('/');
    const building = path[2];
    const floor = path[3];
    const room = path[4];

    if (status === 'Occupied' && event) {
        // Event exists
        dialogTitle.textContent = 'Is this event not happening?';
        dialogMessage.textContent = `Report as cancelled:`;
        eventTitleLabel.style.display = 'none';
        explanationLabel.style.display = 'block';
        confirmButton.textContent = 'Report Cancelled';
        confirmButton.onclick = () => submitReport(building, floor, room, time, 'cancelled');
    } else if (status === 'Available') {
        // Unoccupied slot
        dialogTitle.textContent = `Is there an event in ${building} ${floor}.${room} on ${document.getElementById('schedule-date').value}?`;
        dialogMessage.textContent = 'Let us know:';
        eventTitleLabel.style.display = 'block';
        explanationLabel.style.display = 'none';
        confirmButton.textContent = 'Add Event';
        confirmButton.onclick = () => submitReport(building, floor, room, time, 'add');
    } else if (status === 'Occupied' && !event) {
        // User-submitted event
        dialogTitle.textContent = 'Is this user-reported event not happening?';
        dialogMessage.textContent = 'Confirm event removal:';
        eventTitleLabel.style.display = 'none';
        explanationLabel.style.display = 'none';
        confirmButton.textContent = 'Remove Event';
        confirmButton.onclick = () => submitReport(building, floor, room, time, 'remove');
    }

    dialog.style.display = 'flex';

    document.getElementById('dialog-cancel').onclick = () => {
        dialog.style.display = 'none';
    };
}

async function submitReport(building, floor, room, time, reportType) {
    const eventTitle = document.getElementById('event-title')?.value || '';
    const explanation = document.getElementById('explanation')?.value || '';
    const response = await fetch('/api/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `building=${building}&floor=${floor}&room=${room}&time_block=${time}&report_type=${reportType}&event_title=${eventTitle}&explanation=${explanation}`
    });
    const result = await response.json();
    alert(`Report status: ${result.status}`);
    document.getElementById('report-dialog').style.display = 'none';
    loadSchedule(); // Refresh schedule
}