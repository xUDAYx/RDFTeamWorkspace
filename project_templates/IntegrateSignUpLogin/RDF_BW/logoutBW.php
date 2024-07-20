<?php
session_start();
header('Content-Type: application/json');

// Check if session is properly started
if (session_status() !== PHP_SESSION_ACTIVE) {
    echo json_encode(['status' => 'error', 'message' => 'Unable to start session']);
    exit();
}

// Get the device logout time from the request
$requestPayload = file_get_contents('php://input');
$requestData = json_decode($requestPayload, true);
$deviceLogoutTime = $requestData['deviceLogoutTime'] ?? date('Y-m-d H:i:s');

// Check if the user is logged in
if (isset($_SESSION['email'])) {
    $email = $_SESSION['email'];

    // Call BVO.php to handle logout logic
    include '../RDF_BVO/logoutBVO.php'; // Adjust path as necessary
    include '../RDF_BVO/loginBVO.php'; // Adjust path as necessary
    $response = logLogoutTime($email, $deviceLogoutTime);
    
    if ($response['status'] === 'success') {
        // Destroy the session after logging out
        session_destroy();
    }

    echo json_encode($response);
} else {
    echo json_encode(['status' => 'error', 'message' => 'User not logged in']);
}
?>
