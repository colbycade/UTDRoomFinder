document.addEventListener('DOMContentLoaded', () => {
    const scheduleDate = document.getElementById('schedule-date');
    if (scheduleDate) {
        scheduleDate.addEventListener('change', loadSchedule);
        loadSchedule(); // Initial load
    }

    const reportMissingEvent = document.getElementById('report-missing-event');
    if (reportMissingEvent) {
        reportMissingEvent.addEventListener('click', () => showReportDialog(null, 'add-missing'));
    }

    const prevDayButton = document.getElementById('prev-day');
    const nextDayButton = document.getElementById('next-day');
    if (prevDayButton && nextDayButton) {
        prevDayButton.addEventListener('click', () => changeDate(-1));
        nextDayButton.addEventListener('click', () => changeDate(1));
    }
});

async function loadSchedule() {
    const path = window.location.pathname.split('/').filter(Boolean);
    const building = path[1];
    const room = path[2];
    const date = document.getElementById('schedule-date').value;
    const response = await fetch(`/api/schedule/${building}/${room}`);
    const schedule = await response.json();
    const scheduleTable = document.getElementById('schedule');
    scheduleTable.innerHTML = '';

    if (!schedule[date] || schedule[date].length === 0) {
        scheduleTable.innerHTML = '<tr><td colspan="5">No events scheduled.</td></tr>';
        return;
    }

    // Sort schedule by start_time
    const sortedSchedule = schedule[date].sort((a, b) => {
        return a.start_time.localeCompare(b.start_time);
    });

    sortedSchedule.forEach(slot => {
        const tr = document.createElement('tr');
        const time_block = `${slot.start_time} - ${slot.end_time}`;
        tr.innerHTML = `
            <td>${time_block}</td>
            <td>${slot.status}</td>
            <td>${slot.event_title || ''}</td>
            <td>${slot.notes || ''}</td>
            <td>
                <button class="report-change" start-time="${slot.start_time}" end-time="${slot.end_time}" data-status="${slot.status}" data-event="${slot.event_title || ''}">
                    Report Change
                </button>
            </td>
        `;
        scheduleTable.appendChild(tr);
    });

    document.querySelectorAll('.report-change').forEach(button => {
        button.addEventListener('click', () => showReportDialog(button));
    });
}

// Function to change the date to the next or previous weekday
function changeDate(days) {
    const dateInput = document.getElementById('schedule-date');
    const [year, month, day] = dateInput.value.split('-');
    const currentDate = new Date(year, month - 1, day); // Month is 0-indexed
  
    // Calculate the new date
    currentDate.setDate(currentDate.getDate() + days);
  
    // Skip weekends (Saturday: 6, Sunday: 0)
    if (currentDate.getDay() === 6) { // Skip to Monday if next day is Saturday
      currentDate.setDate(currentDate.getDate() + (days > 0 ? 2 : -1)); 
    } else if (currentDate.getDay() === 0) { // Go back to Friday if previous day is Sunday
      currentDate.setDate(currentDate.getDate() + (days > 0 ? 1 : -2)); 
    }
  
    const newDate = currentDate.toISOString().split('T')[0]; // Format as YYYY-MM-DD
    dateInput.value = newDate;
    loadSchedule();
  }

function showReportDialog(button, mode = 'report') {
    // Get DOM elements
    const dialog = document.getElementById('report-dialog');
    const dialogTitle = document.getElementById('dialog-title');
    const dialogMessage = document.getElementById('dialog-message');
    const eventTitleLabel = document.getElementById('event-title-label');
    const startTimeLabel = document.getElementById('start-time-label');
    const endTimeLabel = document.getElementById('end-time-label');
    const notesLabel = document.getElementById('notes-label');
    const confirmButton = document.getElementById('dialog-confirm');

    // Extract building and room from the URL path
    const [_, building, room] = window.location.pathname.split('/').filter(Boolean);

    // Reset form field visibility and values
    const resetFormFields = () => {
        eventTitleLabel.style.display = 'none';
        startTimeLabel.style.display = 'none';
        endTimeLabel.style.display = 'none';
        notesLabel.style.display = 'none';

        // Clear input values
        document.getElementById('event-title').value = '';
        document.getElementById('start-time').value = '';
        document.getElementById('end-time').value = '';
        document.getElementById('notes').value = '';
    };
    resetFormFields();

    // Configure dialog based on mode or event status
    const config = {
        title: '',
        message: '',
        showEventTitle: false,
        showTimeFields: false,
        showNotes: false,
        confirmText: '',
        reportType: ''
    };

    // For storing reference to the original event
    let eventData = {
        startTime: '',
        endTime: '',
        title: ''
    };

    if (mode === 'add-missing') {
        // Mode: Add a missing event
        config.title = `Is there an event in ${building} ${room} on ${document.getElementById('schedule-date').value}?`;
        config.message = 'Let us know:';
        config.showEventTitle = true;
        config.showTimeFields = true;
        config.showNotes = true;
        config.confirmText = 'Add Event';
        config.reportType = 'add';
    } else {
        // Mode: Report a change to an existing event   
        const status = button.dataset.status;

        // Store the original event details     
        eventData.title = button.dataset.event;
        eventData.startTime = button.getAttribute('start-time');
        eventData.endTime = button.getAttribute('end-time');

        // Set hidden form fields to match the event's data
        document.getElementById('start-time').value = eventData.startTime;
        document.getElementById('end-time').value = eventData.endTime;
        document.getElementById('event-title').value = eventData.title;

        if (status === 'Scheduled') {
            config.title = 'Is this event not happening?';
            config.message = 'Report as cancelled:';
            config.showNotes = true;
            config.confirmText = 'Report Cancelled';
            config.reportType = 'cancelled';
        } else if (status === 'User Reported') {
            config.title = 'Is this user-reported event not happening?';
            config.message = 'Confirm event removal:';
            config.confirmText = 'Remove Event';
            config.reportType = 'remove';
        } else if (status === 'Cancelled') {
            config.title = 'This event was reported as cancelled by a user.';
            config.message = 'Is this event still happening?';
            config.showNotes = true;
            config.confirmText = 'Confirm Event';
            config.reportType = 'uncancel';
        }
    }

    // Apply configuration to the dialog
    dialogTitle.textContent = config.title;
    dialogMessage.textContent = config.message;
    eventTitleLabel.style.display = config.showEventTitle ? 'block' : 'none';
    startTimeLabel.style.display = config.showTimeFields ? 'block' : 'none';
    endTimeLabel.style.display = config.showTimeFields ? 'block' : 'none';
    notesLabel.style.display = config.showNotes ? 'block' : 'none';
    confirmButton.textContent = config.confirmText;
    confirmButton.onclick = () => submitReport(building, room, config.reportType);

    // Show the dialog
    dialog.style.display = 'flex';

    // Handle dialog cancellation
    document.getElementById('dialog-cancel').onclick = () => {
        dialog.style.display = 'none';
    };
}

async function submitReport(building, room, reportType) {
    // Collect form data
    const eventTitle = document.getElementById('event-title')?.value || '';
    const startTime = document.getElementById('start-time')?.value || '';
    const endTime = document.getElementById('end-time')?.value || '';
    const notes = document.getElementById('notes')?.value || '';
    const date = document.getElementById('schedule-date').value; //YYYY-MM-DD

    // Use URLSearchParams to properly encode the form data
    const formData = new URLSearchParams();
    formData.append('building', building);
    formData.append('room', room);
    formData.append('start_time', startTime);
    formData.append('end_time', endTime);
    formData.append('report_type', reportType);
    formData.append('event_title', eventTitle);
    formData.append('notes', notes);
    formData.append('date', date);

    // Submit the report
    const response = await fetch('/api/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString()
    });

    const result = await response.json();
    if (result.error) {
        alert(`Error: ${result.error}`);
    } else {
        alert(`Report status: ${result.status}`);
    }

    // Close the dialog and refresh the schedule
    document.getElementById('report-dialog').style.display = 'none';
    loadSchedule();
}