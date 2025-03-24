document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(searchForm);
            const response = await fetch('/api/search', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            displayResults(data.rooms);
        });
    }

    const scheduleDate = document.getElementById('schedule-date');
    if (scheduleDate) {
        scheduleDate.addEventListener('change', loadSchedule);
        loadSchedule(); // Initial load
    }

    const reportButton = document.getElementById('report-error');
    if (reportButton) {
        reportButton.addEventListener('click', () => alert('Report functionality TBD'));
    }
});

function displayResults(rooms) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<h2>Search Results</h2>';
    if (rooms.length === 0) {
        resultsDiv.innerHTML += '<p>No rooms available.</p>';
    } else {
        const ul = document.createElement('ul');
        rooms.forEach(room => {
            const li = document.createElement('li');
            li.textContent = `${room.room} (${room.building})`;
            const scheduleBtn = document.createElement('button');
            scheduleBtn.textContent = 'View Schedule';
            scheduleBtn.onclick = () => window.location.href = `/schedule/${room.room}`;
            li.appendChild(scheduleBtn);
            ul.appendChild(li);
        });
        resultsDiv.appendChild(ul);
    }
}

async function loadSchedule() {
    const room = window.location.pathname.split('/').pop();
    const date = document.getElementById('schedule-date').value;
    const response = await fetch(`/api/schedule/${room}`);
    const schedule = await response.json();
    const scheduleDiv = document.getElementById('schedule');
    scheduleDiv.innerHTML = schedule[date] ? schedule[date].join('<br>') : 'No events scheduled.';
}