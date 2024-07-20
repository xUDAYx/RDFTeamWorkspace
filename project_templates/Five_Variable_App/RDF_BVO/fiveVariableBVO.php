<!-- Name: Anurag Munesh Raut
Roll no.: B4.T3.02
Team Leader: Harika Pedada -->

<?php
function getVariables() {
    $filePath = 'RDF_DATA/fiveVariableData.json';
    if (!file_exists($filePath)) {
        return [
            'name' => 'No Name found', 
            'branch' => 'No Branch found', 
            'city' => 'No City found', 
            'contactNo' => 'No Contact No. found', 
            'email' => 'No Email found'
        ];
    }
    $json = file_get_contents($filePath);
    $data = json_decode($json, true);
    return [
        'name' => $data['name'] ?? 'No Name found',
        'branch' => $data['branch'] ?? 'No Branch found',
        'city' => $data['city'] ?? 'No City found',
        'contactNo' => $data['contactNo'] ?? 'No Contact No. found',
        'email' => $data['email'] ?? 'No Email found'
    ];
}

function updateVariables($name, $branch, $city, $contactNo, $email) {
    $filePath = '../RDF_DATA/fiveVariableData.json';
    $data = [
        'name' => $name,
        'branch' => $branch,
        'city' => $city,
        'contactNo' => $contactNo,
        'email' => $email
    ];
    return file_put_contents(
        $filePath, json_encode($data, JSON_PRETTY_PRINT));
}
?>
