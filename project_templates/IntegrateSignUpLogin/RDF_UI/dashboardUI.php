<table class="section">
    <table style="max-width: 400px; margin: 40px auto; padding: 20px; background-color: #fff; border: 1px solid #ddd; box-shadow: 0 0 10px rgba(0, 0, 0, 0.2), 0 0 20px rgba(0, 0, 0, 0.1); border-radius: 10px;">
    <tr>
            <td colspan="2" style="text-align: right;">
                <button id="logoutButton" style="padding: 10px 20px; background-color: #333; color: #fff; border: none; cursor: pointer; border-radius: 5px;" onclick="logout()">Logout</button>
            </td>
        </tr>    
    <tr>
            <td colspan="2" style="text-align: center;">
                <h2 style="margin-top: 0; color: #333; font-weight: bold;">Dashboard</h2>
            </td>
        </tr>
        <tr>
            <td style="font-size: 1.5em; color: #333; text-align: center;">
                <span id="currentTime"></span>
            </td>
        </tr>
        <tr>
            <td style="font-size: 2em; color: #333; text-align: center;">
                Session ends in <span id="time">00:59</span> seconds
            </td>
        </tr>
        <tr>
            <td colspan="2" style="padding-top: 20px;">
                <div id="userDetails" style="font-size: 1em; color: #333; text-align: center;"></div>
            </td>
        </tr>
    </table>
</table>
<script src="RDF_ACTION/dashboardAction.js"></script>
<script src="RDF_ACTION/logoutAction.js"></script>