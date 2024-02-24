// scripts.js

function printPage() {
    // Hide non-printable content
    document.getElementById('not-printable').style.display = 'none';
    
    window.print();
    
    document.getElementById('not-printable').style.display = 'block';

    window.location.reload();
}


function confirmDelete(item_id) {
    if (confirm("Are you sure you want to delete this item?")) {
        document.getElementById("deleteForm_" + item_id).submit();
    }
}



// AJAX request to check if ELCO number exists before submitting the form
document.getElementById("addItemForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent default form submission
    
    var elcoNummer = document.getElementById("elco_nummer").value;
    
    // Send AJAX request to check if ELCO number exists
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/check_elco_nummer_exists", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.exists) {
                    alert("ELCO number already exists. Please choose a different ELCO number.");
                } else {
                    // If ELCO number does not exist, submit the form
                    document.getElementById("addItemForm").submit();
                }
            } else {
                alert("Error checking ELCO number existence. Please try again.");
            }
        }
    };
    xhr.send(JSON.stringify({ elco_nummer: elcoNummer }));
});




window.onload = function() {
    var noteRow = document.getElementById('note-row');
    var containerWidth = noteRow.offsetWidth;
    var fontSize = 30; // Initial font size

    // Check if the text exceeds the available width
    while (noteRow.scrollWidth > containerWidth) {
        // Reduce font size by 1px until it fits
        fontSize--;
        noteRow.style.fontSize = fontSize + 'px';
    }
};



