<!-- Name: Anurag Munesh Raut
Roll no.: B4.T3.02
Team Leader: Harika Pedada -->

<?php
include("../RDF_BVO/fiveVariableBVO.php");

if ($_SERVER["REQUEST_METHOD"] == "GET" && isset($_GET["name"]) && isset($_GET["branch"]) && isset($_GET["city"]) && isset($_GET["contactNo"]) && isset($_GET["email"])) {
    $name = $_GET["name"];
    $branch = $_GET["branch"];
    $city = $_GET["city"];
    $contactNo = $_GET["contactNo"];
    $email = $_GET["email"];
    updateVariables($name, $branch, $city, $contactNo, $email);
}

// Redirect to the UI
header('Location: ../RDFView.php');
exit();
?>
