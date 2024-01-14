document.getElementById("view-result-btn").addEventListener("click", function () {
    document.getElementById("view-result-btn").disabled = true;

    // Display loading overlay
    document.getElementById("loading-overlay").style.display = "flex";

    // Perform AJAX request to trigger the conversion and wait for completion
    fetch('/view_result', {
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        // Hide loading overlay
        document.getElementById("loading-overlay").style.display = "none";

        // Check the status of the processing
        if (data.status === 'success') {
            // Redirect to the result page after successful processing
            window.location.href = '/result.html';

        } else {
            // Handle error case
            console.error('Error:', data.message);
            document.getElementById("view-result-btn").disabled = false;
        }
    })
    .catch(error => {
        // Hide loading overlay
        document.getElementById("loading-overlay").style.display = "none";

        console.error('Error:', error);
        document.getElementById("view-result-btn").disabled = false;
    });
});