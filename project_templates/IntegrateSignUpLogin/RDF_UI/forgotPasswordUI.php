<table class="section">
  <table style="max-width: 400px; margin: 40px auto; padding: 20px; background-color: #fff; border: 1px solid #ddd; box-shadow: 0 0 10px rgba(0, 0, 0, 0.2), 0 0 20px rgba(0, 0, 0, 0.1); border-radius: 10px; font-family:Cambria, Cochin, Georgia, Times, 'Times New Roman', serif;">
    <tr>
      <td colspan="2" style="text-align: center;">
        <h2 style="margin-top: 0; color: #333; font-weight: bold;">Forgot Password</h2>
      </td>
    </tr>
    <tr>
      <td colspan="2" style="text-align: center;">
        <div id="generalError" style="color: red; font-size: 0.9em;"></div>
      </td>
    </tr>
    <tr>
      <td><label for="email">Email :</label></td>
      <td><input type="text" id="email" name="email" autocomplete="email" style="width: 90%; padding: 10px; border: 1px solid #ccc; border-radius: 5px;"></td>
    </tr>
    <tr>
      <td colspan="2" style="text-align: center;">
        <div id="emailError" style="color: red; font-size: 0.9em;"></div>
      </td>
    </tr>
    <tr>
      <td colspan="2" style="text-align: center; padding-top: 10px;">
        <button type="button" onclick="reset()" style="padding: 10px 20px; border: 0.5px solid grey; border-radius: 10px; cursor: pointer; font-family:Cambria, Cochin, Georgia, Times, 'Times New Roman', serif;">Reset Password</button>
      </td>
    </tr>
    <tr>
      <td colspan="2" style="text-align: center;">
        <div id="loader" style="display: none; font-size: 1.2em; color: #333;">Loading...</div>
      </td>
    </tr>
  </table>
</table>
<script src="RDF_ACTION/forgotPasswordAction.js"></script>
