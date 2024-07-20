<table class="section">
    <table style="max-width: 400px; margin: 40px auto; padding: 20px; background-color: #fff; border: 1px solid #ddd; box-shadow: 0 0 10px rgba(0, 0, 0, 0.2), 0 0 20px rgba(0, 0, 0, 0.1); border-radius: 10px; font-family:Cambria, Cochin, Georgia, Times, 'Times New Roman', serif;">
        <tr>
            <td colspan="2" style="text-align: center;">
                <h2 style="margin-top: 0; color: #333; font-weight: bold;">Login Screen</h2>
            </td>
        </tr>
        <tr>
            <td colspan="2" style="text-align: center;">
                <div id="loginError" style="color: red; display: none; margin-bottom: 10px;"></div>
            </td>
        </tr>
        <tr>
            <td><label for="email">Email:</label></td>
            <td>
                <input type="email" id="email" name="email" autocomplete="email" style="width: 90%; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
                <div id="emailError" style="color: red; display: none;"></div>
            </td>
        </tr>
        <tr>
            <td><label for="password">Password:</label></td>
            <td style="position: relative;">
                <input type="password" id="password" name="password" autocomplete="current-password" style="width: 90%; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
                <i id="togglePassword" class="toggle-password" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer;">0</i>
                <div id="passwordError" style="color: red; display: none;"></div>
            </td>
        </tr>
        <tr>
            <td colspan="2" style="text-align: center; padding-top: 10px;">
                <button type="button" onclick="login()" style="padding: 10px 20px; border: 0.5px solid grey; border-radius: 10px; cursor: pointer; font-family:Cambria, Cochin, Georgia, Times, 'Times New Roman', serif;">Login</button>
            </td>
        </tr>
        <tr>
        <td colspan="2" style="text-align: center; padding-top: 10px;">
                <a href="RDFView.php?ui=signUpUI">Register</a><br>
                <a href="RDFView.php?ui=forgotPasswordUI">Forgot Password?</a>
            </td>
        </tr>
    </table>
</table>
<script src="RDF_ACTION/loginAction.js"></script>
