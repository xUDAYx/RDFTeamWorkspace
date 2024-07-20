
//http://localhost/projects/ReminderApp/RDFView.php


var modal = document.getElementById("myModal");
var modalText = document.getElementById("modalText");

// Function to display the modal
function openModal(message) {
  modal.style.display = "block";
  modalText.textContent = message;
  playAlertSound();
}

// Function to close the modal
function closeModal() {
  modal.style.display = "none";
  
  
}

// Function to play alert sound
function playAlertSound() {
  var alertSound = document.getElementById("alertSound");
  alertSound.play();
}

var taskNumber = 1;

function setReminder() {
  var reminderInput = document.getElementById("reminder").value;
  var noteInput = document.getElementById("note").value;

  if (reminderInput && noteInput) {
    var reminderTime = new Date(reminderInput).toLocaleString();

    // Display reminder details
    var reminderDetailsTable = document.getElementById("reminderDetailsTable").getElementsByTagName('tbody')[0];
    var newRow = reminderDetailsTable.insertRow();
    var index = newRow.rowIndex; // Get the current row index
    var cell1 = newRow.insertCell(0);
    var cell2 = newRow.insertCell(1);
    var cell3 = newRow.insertCell(2);
    var cell4 = newRow.insertCell(3);
    var cell5 = newRow.insertCell(4); // For delete button
    cell1.textContent = taskNumber++;
    cell2.textContent = reminderTime.split(",")[0]; // Date
    cell3.textContent = reminderTime.split(",")[1]; // Time
    cell4.textContent = noteInput;

    // Add delete button
    var deleteButton = document.createElement("button");
    deleteButton.textContent = "Delete";
    deleteButton.style.padding = "5px 10px";
    deleteButton.style.backgroundColor = "#dc3545";
    deleteButton.style.color = "#fff";
    deleteButton.style.border = "none";
    deleteButton.style.cursor = "pointer";
    deleteButton.style.borderRadius = "4px";
    deleteButton.onclick = function() {
      deleteReminder(index);
    };
    cell5.appendChild(deleteButton);

    var timeDiff = new Date(reminderInput).getTime() - new Date().getTime();

    if (timeDiff > 0) {
      setTimeout(function() {
        openModal("Reminder: " + noteInput);
        // Remove the reminder from the DOM
        deleteReminder(index);
      }, timeDiff);
    } else {
      alert("Please set a future time for the reminder.");
    }
  } else {
    alert("Please enter both reminder time and note.");
  }
}

function deleteReminder(index) {
  var reminderDetailsTable = document.getElementById("reminderDetailsTable").getElementsByTagName('tbody')[0];
  reminderDetailsTable.deleteRow(index - 1); // Adjust index for 0-based rowIndex
}
