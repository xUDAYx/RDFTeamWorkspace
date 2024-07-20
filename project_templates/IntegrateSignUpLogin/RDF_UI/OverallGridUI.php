<style>
    .hidden {
        display: none;
    }

    /* Adjusted CSS for table container */
    #table-container {
        overflow-x: auto;
    }

    table {
        border-collapse: collapse;
        width: 80%;
        max-width: 400px;
        margin: 40px auto;
        padding: 20px;
        background-color: #fff;
        border: 1px solid #ddd;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.2), 0 0 20px rgba(0, 0, 0, 0.1);
        border-radius: 10px;
    }

    table,
    th,
    td {
        border: 1px solid black;
    }

    th,
    td {
        padding: 8px;
        text-align: center;
    }

    th {
        background-color: #f2f2f2;
    }

    .eligible {
        color: green;
    }

    .not-eligible {
        color: orange;
    }

    .terminated {
        color: red;
    }

    .present {
        color: green;
    }

    .absent {
        color: red;
    }

    button {
        padding: 10px 20px;
        cursor: pointer;
    }

    #no-data-message {
        color: red;
        font-weight: bold;
    }
</style>


<!-- Added table container div -->
<div id="table-container">

    <table id="main-page" >
        <!-- <caption style="font-size:30px; font-weight:bold;">Main Page</caption> -->
         <h1 style="text-align: center;">Main Page</h1>
         <tr>
        <td style="text-align: left;">
            <button type="button" onclick="window.location.href = 'RDFView.php?ui=profileCreationUI'" style="padding: 10px 20px; font-size: 14px; background-color: #333; color: #fff; border: none; cursor: pointer; border-radius: 5px; text-decoration: none; display: flex; align-items: center;">
                Profile
            </button>
        </td>
        <td style="text-align: right;">
            <button onclick="window.location.href = 'RDFView.php?ui=loginUI'" style="padding: 10px 20px; font-size: 14px; background-color: #333; color: #fff; border: none; cursor: pointer; border-radius: 5px; text-decoration: none; margin-left: 10px;">Logout</button>
        </td>
    </tr>
         <tr>
        <?php include 'RDF_BVO/dashboardBVO.php'; ?>
        <td colspan="2" style="text-align: center; padding: 20px 0;">
            <h2 class="welcome-message" style="font-size: 1.5em; margin-top: 20px; color: #333; font-weight: bold;">
                Welcome, <?php echo htmlspecialchars(getUserNameFromSession()); ?>!
            </h2>
        </td>
    </tr>
        <tr>
            <td>
                <button id="interns-data-button">Interns Data</button>
            </td>
      
            <td>
                <button id="project-data-button">Project Data</button>
            </td>
        </tr>
    </table>

















    
    <table id="interns-page" class="hidden">
        <caption style="font-size:30px; font-weight:bold;">Interns Attendance and Rating Records</caption>
        <tr>
            <td colspan="8">
                <label for="search-criteria">Search by:</label>
                <select id="search-criteria">
                    <option value="name">Name</option>
                </select>
                <input type="text" id="search-input" placeholder="Enter search term">
                <button id="search-button">Search</button>
                <button id="reset-button" class="hidden">Return to Original Data</button>
            </td>
        </tr>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Attendance (%)</th>
            <th>Rating</th>
            <th>Average (%)</th>
            <th>Status</th>
            <th>Details</th>
        </tr>
        <tbody id="records-body">
            <!-- Data will be dynamically inserted here -->
        </tbody>
        <tfoot>
            <tr>
                <td colspan="7">
                    <button id="back-to-main">Back to Main</button>
                </td>
            </tr>
        </tfoot>
    </table>

    <p id="no-data-message" class="hidden">Data Not Found</p>

    <table id="details-section" class="hidden">
        <caption style="font-size:30px; font-weight:bold;">Details Section</caption>
        <tr>
            <td>
                <table id="attendance-details">
                    <caption>Attendance and Rating Details</caption>
                    <thead>
                        <tr>
                            <th>Date(YYYY-MM-DD)</th>
                            <th>Attendance</th>
                            <th>Rating</th>
                        </tr>
                    </thead>
                    <tbody id="details-body">
                        <!-- Attendance and rating details will be dynamically inserted here -->
                    </tbody>
                </table>
            </td>
        </tr>
        <tr>
            <td>
                <table id="project-details">
                    <caption>Project Details</caption>
                    <thead>
                        <tr>
                            <th>Project Name</th>
                            <th>Leader</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="project-details-body">
                        <!-- Project details will be dynamically inserted here -->
                    </tbody>
                </table>
            </td>
        </tr>
        <tr>
            <td>
                <button id="back-to-interns-from-details">Back to Interns</button>
            </td>
        </tr>
    </table>

    <table id="projects-page" class="hidden">
        <caption style="font-size:30px; font-weight:bold;">Project Data</caption>
        <tr></tr>
        <tr>
            <th>Project ID</th>
            <th>Project Name</th>
            <th>Description</th>
            <th>Status</th>
            <th>Leader</th>
            <th>Intern1</th>
            <th>Intern2</th>
            <th>Intern3</th>
            <th>Squad Member</th>
            <th>Start Date</th>
            <th>End Date</th>
        </tr>
        <tbody id="projects-body">
            <!-- Project data will be dynamically inserted here -->
        </tbody>
        <tfoot>
            <tr>
                <td colspan="11">
                    <button id="back-to-main-from-projects">Back to Main</button>
                </td>
            </tr>
        </tfoot>
    </table>

</div> <!-- End of table-container -->

<script src="RDF_ACTION/OverallGridACTION.js"></script>