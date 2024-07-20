<table class="section">
    <table style="max-width: 400px; margin: 40px auto; padding: 20px; background-color: #fff; border: 1px solid #ddd; box-shadow: 0 0 10px rgba(0, 0, 0, 0.2), 0 0 20px rgba(0, 0, 0, 0.1); border-radius: 10px; font-family: Cambria, Cochin, Georgia, Times, 'Times New Roman', serif;">
        <tr>
            <td colspan="2" style="text-align: center;">
                <h2 style="margin-top: 0; color: #333; font-weight: bold;">Sign Up</h2>
            </td>
        </tr>
        <tr>
            <td><label for="fullName">Full Name:</label></td>
            <td><input type="text" id="fullName" name="fullName" style="width: 90%; padding: 10px; border: 1px solid #ccc; border-radius: 5px;"></td>
        </tr>
        <tr>
            <td><label for="email">Email:</label></td>
            <td>
                <input type="email" id="email" name="email" autocomplete="email" style="width: 90%; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
                <span id="emailError" style="color: red;"></span>
            </td>
        </tr>
        <tr>
            <td><label for="mobile">Mobile Number:</label></td>
            <td>
                <input type="tel" id="mobile" name="mobile" style="width: 90%; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
                <span id="mobileError" style="color: red;"></span>
            </td>
        </tr>
        <tr>
            <td><label for="password">Password:</label></td>
            <td style="position: relative;">
                <input type="password" id="password" name="password" autocomplete="new-password" style="width: 90%; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
                <i class="toggle-password" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer;">o</i>
                <span id="passwordError" style="color: red;"></span>
            </td>
        </tr>
        <tr>
            <td><label for="confirmPassword">Confirm Password:</label></td>
            <td style="position: relative;">
                <input type="password" id="confirmPassword" name="confirmPassword" autocomplete="new-password" style="width: 90%; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
                <i class="toggle-password" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer;">o</i>
                <span id="confirmPasswordError" style="color: red;"></span>
            </td>
        </tr>
        <tr>
            <td colspan="2" style="text-align: center; padding-top: 10px;">
                <button type="button" onclick="signUp()" style="font-family:Cambria, Cochin, Georgia, Times, 'Times New Roman', serif; padding: 10px 20px; border:0.5px solid grey; border-radius: 10px; cursor: pointer;">Sign Up</button>
            </td>
        </tr>
        <tr>
            <td colspan="2" style="text-align: center; padding-top: 10px;">
                <p>Already have an account?</p>
                <a href="RDFView.php?ui=loginUI">Login here</a>
            </td>
        </tr>
    </table>
</table>
<script src="RDF_ACTION/signUpAction.js"></script>
