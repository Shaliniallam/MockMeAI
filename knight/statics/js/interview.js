document.getElementById("submit-button").addEventListener("click", function (event) {
    event.preventDefault(); // Prevent the default form submission

    document.getElementById("loading-overlay").style.display = "block";
    document.getElementById("loading-spinner").style.display = "block";


    // Get form data
    var formData = new FormData(document.getElementById("input-data"));
     // Perform AJAX submission
     fetch('/submit_application', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Handle the response if needed
            document.getElementById("loading-overlay").style.display = "none";
            document.getElementById("loading-spinner").style.display = "none";
            console.log(data);

            if (data && data.status === "success") {
        // Check if the response includes the next question number
        
            // Redirect to the next question
            window.location.href = '/questions.html/1';
        }

        })
        .catch(error => {
            document.getElementById("loading-overlay").style.display = "none";
            document.getElementById("loading-spinner").style.display = "none";
            console.error('Error:', error);
        });
});
