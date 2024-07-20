<?php
session_start();

header('Content-Type: application/json');
require '../RDF_BVO/dashboardBVO.php';

class UserService {
    public function getUserDetails($email) {
        $user = new User();
        return $user->fetchUserByEmail($email);
    }
}

// Check if the user is logged in by verifying the session
if (isset($_SESSION['email'])) {
    $loggedInEmail = $_SESSION['email'];

    $userService = new UserService();
    $userDetails = $userService->getUserDetails($loggedInEmail);

    if ($userDetails) {
        echo json_encode($userDetails);
    } else {
        echo json_encode(['message' => 'User not found']);
    }
} else {
    echo json_encode(['message' => 'User is not logged in']);
}


?>
