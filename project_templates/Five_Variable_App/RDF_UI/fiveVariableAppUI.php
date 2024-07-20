<!-- Name: Anurag Munesh Raut
Roll no.: B4.T3.02
Team Leader: Harika Pedada -->
<!-- Connecting BVO to UI -->
<?php 
    include "RDF_BVO/fiveVariableBVO.php";
    $variables = getVariables();
?>
<!-- Ends -->

<!-- The UI -->

<h2>Enter New Values</h2>
<form>
    <table>
        <tr>
            <td><label for="name">Name:</label></td>
        </tr>
        <tr>
            <td><input type="text" id="name" name="name"></td>
        </tr>
        <tr>
            <td><label for="branch">Branch:</label></td>
        </tr>
        <tr>
            <td><input type="text" id="branch" name="branch"></td>
        </tr>
        <tr>
            <td><label for="city">City:</label></td>
        </tr>
        <tr>
            <td><input type="text" id="city" name="city"></td>
        </tr>
        <tr>
            <td><label for="contactNo">Contact No.:</label></td>
        </tr>
        <tr>
            <td><input type="text" id="contactNo" name="contactNo"></td>
        </tr>
        <tr>
            <td><label for="email">Email:</label></td>
        </tr>
        <tr>
            <td><input type="text" id="email" name="email"></td>
        </tr>
        <tr>
            <td>
                <button type="button" onclick="updateVarsAction()">Update Variables</button>
            </td>
        </tr>
    </table>
</form>

<h2>Current Values from the DB</h2>
<h3>Name: <?php echo $variables['name']; ?></h3>
<h3>Branch: <?php echo $variables['branch']; ?></h3>
<h3>City: <?php echo $variables['city']; ?></h3>
<h3>Contact No.: <?php echo $variables['contactNo']; ?></h3>
<h3>Email: <?php echo $variables['email']; ?></h3>
<!-- Ends -->

<!-- Connecting UI to Action-->
<script src="RDF_ACTION/updateFiveVariableAction.js"></script>
<!-- Ends -->

