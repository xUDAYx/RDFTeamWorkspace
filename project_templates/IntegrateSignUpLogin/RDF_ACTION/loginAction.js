function validateEmail(email) {
    const emailPattern = /^[^\d][\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/;
    return emailPattern.test(email);
}

function validatePassword(password) {
    const passwordPattern = /^(?=.*[!@#$%^&*(),.?":{}|<>])(?=.*\d).{8,}$/;
    return passwordPattern.test(password);
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.style.display = 'block';
}

function hideError(elementId) {
    const element = document.getElementById(elementId);
    element.style.display = 'none';
}

function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const deviceTime = new Date().toLocaleString('sv-SE');
     // Get device time in Y-m-dTH:i:s format
    let isValid = true;

    hideError('emailError');
    hideError('passwordError');
    hideError('loginError');

    // Check if email is empty
    if (email.trim() === '') {
        showError('emailError', 'Email is required.');
        isValid = false;
    } else if (!validateEmail(email)) {
        showError('emailError', 'Enter a valid email.');
        isValid = false;
    }

    // Check if password is empty
    if (password.trim() === '') {
        showError('passwordError', 'Password is required.');
        isValid = false;
    } else if (!validatePassword(password)) {
        showError('passwordError', 'Password must be at least 8 characters long, contain at least one special symbol and one number.');
        isValid = false;
    }

    if (!isValid) {
        return;
    }

    fetch(`RDF_BW/loginBW.php?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}&deviceTime=${encodeURIComponent(deviceTime)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
                window.location.href = "RDFView.php?ui=dashboardUI";
            } else {
                showError('loginError', data.message);
            }
        })
        .catch(error => {
            console.error('Fetch Error:', error);
            showError('loginError', 'User is not Registered.');
        });
}

document.addEventListener('DOMContentLoaded', function() {
    const togglePassword = document.getElementById('togglePassword');
    const passwordField = document.getElementById('password');

    togglePassword.addEventListener('click', function() {
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
            togglePassword.textContent = 'o';
        } else {
            passwordField.type = 'password';
            togglePassword.textContent = 'o';
        }
    });
});
