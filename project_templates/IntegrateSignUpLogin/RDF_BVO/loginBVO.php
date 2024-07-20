<?php
function checkCredentials($email, $password, $deviceTime) {
    $file = '../RDF_DATA/signUpDetailsData.json';

    if (!file_exists($file)) {
        return ['status' => 'error', 'message' => 'No user data found'];
    }

    $fileContents = file_get_contents($file);

    if ($fileContents === false) {
        return ['status' => 'error', 'message' => 'Error reading user data'];
    }

    if (empty($fileContents)) {
        return ['status' => 'error', 'message' => 'User file data is empty'];
    }

    $current_data = json_decode($fileContents, true);

    if ($current_data === null) {
        return ['status' => 'error', 'message' => 'Error decoding user data'];
    }

    foreach ($current_data as $user) {
        if ($user['email'] === $email) {
            if ($user['password'] === $password) {
                // Save the login data with email, password, id, and times
                saveLoginData($user['id'], $email, $password, $deviceTime);

                return [
                    'status' => 'success',
                    'message' => 'User Login Is Successful.',
                    'user' => [
                        'id' => $user['id'],
                        'email' => $user['email'],
                        'fullName' => $user['fullName'],
                        'mobile' => $user['mobile']
                    ]
                ];
            } else {
                return ['status' => 'error', 'message' => 'Incorrect password.'];
            }
        }
    }

    return ['status' => 'error', 'message' => 'User is not Registered.'];
}

function saveLoginData($id, $email, $password, $deviceTime) {
    $loginDataFile = '../RDF_DATA/loginData.json';

    // Read the existing login data
    if (file_exists($loginDataFile)) {
        $loginDataContents = file_get_contents($loginDataFile);
        $loginData = $loginDataContents ? json_decode($loginDataContents, true) : [];
    } else {
        $loginData = [];
    }

    // Explicitly set timezone to 'UTC' (or the appropriate timezone of your application)
    date_default_timezone_set('UTC');

    // Calculate logout time as 30 seconds from login time
    $loginTime = strtotime($deviceTime);
    $sessionLogoutTime = date('Y-m-d H:i:s', $loginTime + 60);

    // Restore the default timezone if needed
    date_default_timezone_set(date_default_timezone_get());

    $loginData[] = [
        'id' => $id,
        'email' => $email,
        'password' => $password,
        'loginTime' => $deviceTime,
        'logoutTime' => $sessionLogoutTime  // Adding calculated logout time
    ];

    // Save the updated login data with pretty print
    file_put_contents($loginDataFile, json_encode($loginData, JSON_PRETTY_PRINT));
}
?>
