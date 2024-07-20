<?php
session_start();
include '../RDF_BVO/loginBVO.php';
header('Content-Type: application/json');

// Check if session is properly started
if (session_status() !== PHP_SESSION_ACTIVE) {
    echo json_encode(['status' => 'error', 'message' => 'Unable to start session']);
    exit();
}

if (isset($_GET['email']) && isset($_GET['password']) && isset($_GET['deviceTime'])) {
    $email = filter_var($_GET['email'], FILTER_SANITIZE_EMAIL);
    $password = $_GET['password']; // Password should be validated, but not sanitized the same way as email
    $deviceTime = $_GET['deviceTime']; // Get the device time

    $response = checkCredentials($email, $password, $deviceTime);
    
    if ($response['status'] === 'success') {
        $_SESSION['email'] = $email;  // Store the email in the session
    }
    
    echo json_encode($response);
} else {
    echo json_encode(['status' => 'error', 'message' => 'Invalid input']);
}
?>
