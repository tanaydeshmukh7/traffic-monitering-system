
async function updateDashboard() {
    try {
        const response = await fetch("/api/traffic");

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        console.log("Traffic API connected:", data);

        // Update dashboard elements
        const updateText = (id, value) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        };

        updateText("vehicle-count", data.vehicle_count);
        updateText("violation-count", data.violation_count);
        updateText("traffic-density", data.density);
        updateText("signal-status", data.signal);
        updateText("system-status", data.system_status);

    } catch (error) {
        console.error("Dashboard API error:", error);
        updateText("system-status", "OFFLINE");
    }
}

updateDashboard();
setInterval(updateDashboard, 1000);
