function logout() {
    // Capture the current device time
    const deviceLogoutTime = new Date().toLocaleString('sv-SE');

    // Fetch the bw.php file to perform the logout and get the response
    fetch('RDF_BW/logoutBW.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ deviceLogoutTime }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Display success popup with logout time
            alert(`${data.message} at ${data.logoutTime}`);
            
            // Redirect to login page after successful logout
            window.location.href = "RDFView.php?ui=loginUI";
        } else {
            // Display failure popup
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Handle any errors that occurred during fetch
        alert('An error occurred during logout');
    });
}
