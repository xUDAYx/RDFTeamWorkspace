// Name: Anurag Munesh Raut
// Roll no.: B4.T3.02
// Team Leader: Harika Pedada

// Action Called Here
function updateVarsAction() {
    const name = document.getElementById('name').value;
    const branch = document.getElementById('branch').value;
    const city = document.getElementById('city').value;
    const contactNo = document.getElementById('contactNo').value;
    const email = document.getElementById('email').value;
    alert("Variables are updated in JSON");

    // Connecting Action to the Business Workflow (BW)
    const URLtoBW = "RDF_BW/updateFiveVariableBW.php?name=" + name + "&branch=" + branch + "&city=" + city + "&contactNo=" + contactNo + "&email=" + email;

    window.location.href = URLtoBW;
}
