function startTimer(duration, display) {
    let timer = duration, minutes, seconds;
    setInterval(function () {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (--timer < 0) {
            window.location.href = "RDFView.php?ui=loginUI";
        }
    }, 1000);
}

function updateTime() {
    const now = new Date();
    const hours = now.getHours() < 10 ? "0" + now.getHours() : now.getHours();
    const minutes = now.getMinutes() < 10 ? "0" + now.getMinutes() : now.getMinutes();
    const seconds = now.getSeconds() < 10 ? "0" + now.getSeconds() : now.getSeconds();
    const currentTimeString = hours + ":" + minutes + ":" + seconds;
    document.getElementById('currentTime').textContent = currentTimeString;
}

function fetchUserDetails() {
    fetch('RDF_BW/dashboardBW.php')  // Ensure this endpoint is correct
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                document.getElementById('userDetails').textContent = data.message;
            } else {
                document.getElementById('userDetails').innerHTML = `
                    <p><strong>Full Name:</strong> ${data.fullName}</p>
                    <p><strong>Email:</strong> ${data.email}</p>
                `;
            }
        })
        .catch(error => console.error('Error:', error));
}

window.onload = function () {
    const thirtySeconds = 60,
        display = document.querySelector('#time');
    startTimer(thirtySeconds, display);
    setInterval(updateTime, 1000);
    updateTime(); // Initialize the current time immediately

    // Fetch user details on load
    fetchUserDetails();
};
