document.addEventListener("DOMContentLoaded", function () {
    const eventsList = document.getElementById("events-list");

    async function fetchEvents() {
        const response = await fetch("/events");
        const events = await response.json();

        eventsList.innerHTML = ""; // Clear the list
        events.forEach(event => {
            const li = document.createElement("li");
            li.textContent = event.message;
            eventsList.appendChild(li);
        });
    }

    // Fetch events every 15 seconds
    setInterval(fetchEvents, 15000);
    fetchEvents(); // Initial fetch
});
