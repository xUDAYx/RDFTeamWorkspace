<!-- 
Online HTML, CSS and JavaScript editor to run code online.
-->

<?php

function startBottomNavigationBar(){
  echo '<div class="navbar">';
}

function addLink($href, $class,$linkText){
  echo '<a href="'.$href.'" class="'.$class.'">'.$linkText.'</a>';
}

function endBottomNavigationBar(){
  echo '</div>';
}

function startContainer(){
  echo '<div class="container">';
}

function endContainer(){
  echo '</div">';
}

function startTable(){
  echo '<table class="section">';
}

function endTable(){
  echo '</table>';
}

function row(){
  echo "</tr><tr>";
}

function addCell($colspan, $bgColor, $content){
  echo '<td colspan="'.$colspan.'" style="background-color:'.$bgColor.'">'.$content.'</td>';
}

$uiFilePath="";

if(isset($_GET['UI']))
{
  echo "<hr>";
  print_r($_GET);
  $uiFileName=$_GET['UI'];
  $uiFileName = 'RDF_UI/'.$uiFileName.'.php';
  echo $uiFilePath;
  echo "<hr>";
  exit();
}else if(isset($_GET['ui']))
{
  //echo "<hr>";
  //print_r($_GET);
  $uiFileName=$_GET['ui'];
  $uiFilePath = 'RDF_UI/'.$uiFileName.'.php';
  //echo "File Name is : ".$uiFilePath;
  //echo "<hr>";
  
}
else{
  Echo "<h1>Mention UI Template File Name</h1>";
  exit();
}

?>

<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  
  <title>RDF App</title>
  <style>

    body {
            font-size: 1.5em; /* Base font size */
            margin: 0;
            background-color: white;
            color:gray;

         }
    table {
            border-collapse: collapse;
            width: 100%;
            margin: 0;
            padding: 0;
            border-collapse: separate;
            border-spacing: 5px;
          }
    table, th, td {
            text-align: center;
            padding: 0; /* Padding for readability */
            margin: 0;
            text-align:left;
          }
    
    .container {
      max-width: 800px;
      margin: 0 auto;
      font-family: Arial, sans-serif;
      padding: 20px;
    }
    h1{
      margin:0px;
    }

    

    button.greenbutton{
      font-size:1em;
      background-color:#04AA6D;
      color:white;
      border-radius: 5px;
      width: 100%;
    }

    button.blackbutton{
      font-size:1em;
      background-color:#17202a;
      color:white;
      border-radius: 5px;
      width: 100%;
    }

    button.graybutton{
      font-size:1em;
      background-color:#808b96;
      color:white;
      border-radius: 5px;
      width: 100%;
    }

    button.redbutton{
      font-size:1em;
      background-color:#e74c3c;
      color:white;
      border-radius: 5px;
      width: 100%;
    }

    button.bluebutton{
      font-size:1em;
      background-color:#2e86c1;
      color:white;
      border-radius: 5px;
      width: 100%;
    }

    button.magentabutton{
      font-size:1em;
      background-color:#a569bd;
      color:white;
      border-radius: 5px;
      width: 100%;
    }

    input.whiteInput{
      font-size:1em;
      background-color:white;
      color:gray;
      border-radius: 5px;
      width: 100%;
    }

    .navbar {
  overflow: hidden;
  background-color: #333;
  position: fixed;
  bottom: 0;
  width: 100%;
}

.navbar a {
  float: left;
  display: block;
  color: #f2f2f2;
  text-align: center;
  padding: 14px 16px;
  text-decoration: none;
  
}

.navbar a:hover {
  background: #f1f1f1;
  color: black;
}

.navbar a.active {
  background-color: #04AA6D;
  color: white;
}

.main {
  padding: 16px;
  margin-bottom: 30px;
}

    
  </style>

  
</head>

<body>

 <!--  <div style="background-color:black; margin:0px; padding:5px; color:#EAEDED;" >
    Button to toggle the border
    <input type="checkbox" id="myCheckbox" > Show Border
  </div>  -->


  
  

      <?php include($uiFilePath); ?>
   


   <script type="text/javascript">

        setTableBorderForAlltheTables("1px solid white");

          // Get the table and button elements
        var table1 = document.getElementById("myTable");
        var IncreaseTextButton = document.getElementById("IncreaseTextButton");
        var decreaseTextButton = document.getElementById("decreaseTextButton");


        const checkbox = document.getElementById('myCheckbox');
        checkbox.addEventListener('change', function(){
          if (checkbox.checked) {
            //alert("Check Box Checked.......");
            setTableBorderForAlltheTables("1px dotted darkgray");
          }else {
            //alert("Check Box Checked");
            setTableBorderForAlltheTables("1px solid white");
          }
        });


        function setTableBorderForAlltheTables(borderStyle){
          // Get all table elements on the page
          var tables = document.querySelectorAll('table');
          // Loop through each table and apply the desired styles
          tables.forEach(function(table) {
              setTableBorder(table, borderStyle);
          });
        }

        
        function setTableBorder(table, borderStyle){
                 table.style.border = borderStyle; 
                // Get all the cells (both <th> and <td> elements)
                const cells = table.getElementsByTagName('td');
                const headers = table.getElementsByTagName('th');                
                // Combine cells and headers into a single array
                const allCells = Array.from(cells).concat(Array.from(headers));                
                // Loop through each cell and apply the desired style
                allCells.forEach(cell => {
                     cell.style.border = borderStyle;
                });
        }

       

        IncreaseTextButton.addEventListener("click", function () {
            // Call the function to Increase the text size
            IncreaseTextSize();
        });

        decreaseTextButton.addEventListener("click", function () {
            // Call the function to Increase the text size
            decreaseTextSize();
        });
    
    // Function to Increase the font size of all text elements in the page
        function IncreaseTextSize() {
            // Get all text-containing elements
            let elements = document.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6, td, a, b, i, u');
            // Iterate through all the elements and Increase their font size
            elements.forEach(element => {
                // Get the current font size
                let currentFontSize = window.getComputedStyle(element).fontSize;
                // Calculate the new font size
                let newFontSize = parseFloat(currentFontSize) * 1.1;
                // Update the element's font size
                element.style.fontSize = `${newFontSize}px`;
            });
        }

         // Function to Increase the font size of all text elements in the page
        function decreaseTextSize() {
            // Get all text-containing elements
            let elements = document.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6, td, a, b, i, u');
            // Iterate through all the elements and Increase their font size
            elements.forEach(element => {
                // Get the current font size
                let currentFontSize = window.getComputedStyle(element).fontSize;
                // Calculate the new font size
                let newFontSize = parseFloat(currentFontSize) * 0.9;
                // Update the element's font size
                element.style.fontSize = `${newFontSize}px`;
            });
        }

      

  </script>

</body>

</html>