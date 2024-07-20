<?php
function logLogoutTime($email, $logoutTime) {
    $filePath = '../RDF_DATA/loginData.json';

    // Read the existing data from the JSON file
    if (!file_exists($filePath)) {
        return ['status' => 'error', 'message' => 'Data file not found'];
    }

    $data = json_decode(file_get_contents($filePath), true);

    // Flag to check if user is found in data
    $userFound = false;

    // Update the logout time for the user (iterate in reverse to find the last occurrence)
    for ($i = count($data) - 1; $i >= 0; $i--) {
        if ($data[$i]['email'] === $email) {
            $data[$i]['logoutTime'] = $logoutTime; // Update session end time
            $userFound = true;
            break;
        }
    }

    // If user not found in data, return error
    if (!$userFound) {
        return ['status' => 'error', 'message' => 'User not found in data'];
    }

    // Write the updated data back to the JSON file
    if (file_put_contents($filePath, json_encode($data, JSON_PRETTY_PRINT)) !== false) {
        return ['status' => 'success', 'message' => 'Logout Successfully', 'logoutTime' => $logoutTime];
    } else {
        return ['status' => 'error', 'message' => 'Failed to write to data file'];
    }
}
?>
