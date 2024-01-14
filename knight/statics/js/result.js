document.addEventListener('DOMContentLoaded', function () {
    // Counter to keep track of the current question
    let currentQuestionIndex = 0;

    // Function to fetch interview results from the server with audio
    function getInterviewResultsWithAudio() {
        // Show loading container while waiting for results
        document.getElementById('loading-container').style.display = 'block';

        // Make a GET request to the server endpoint for results with audio
        fetch('/get_interview_results_with_audio', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            // Check the response status
            if (data.status === 'success') {
                // Display results dynamically
                displayResultsWithAudio(data.results);
            } else {
                console.error('Error fetching interview results with audio:', data.message);
            }
        })
        .catch(error => {
            console.error('Error fetching interview results with audio:', error);
        })
        .finally(() => {
            // Hide loading container regardless of success or failure
            document.getElementById('loading-container').style.display = 'none';
        });
    }

    // Function to display interview results with audio dynamically
    function displayResultsWithAudio(results) {
        const resultsContainer = document.getElementById('results');

        // Clear existing content
        resultsContainer.innerHTML = '';

        // Check if there are more questions to display
        if (currentQuestionIndex < results.length) {
            const result = results[currentQuestionIndex];

            // Create HTML elements for the current question, answer, and audio
            const questionDiv = document.createElement('div');
            questionDiv.className = 'question';
            questionDiv.textContent = `Question ${currentQuestionIndex + 1}: ${result.question}`;

            const answerDiv = document.createElement('div');
            answerDiv.className = 'answer';
            answerDiv.textContent = `Your Response ${result.answer}`;

            const audioDiv = document.createElement('div');
            audioDiv.className = 'audio';

            // Check if the audio file exists for the current question
            if (result.audio_exists) {
                const audioElement = document.createElement('audio');
                audioElement.controls = true;
                audioElement.src = `/audio/${result.audio_path}`;
                audioElement.type = 'audio/wav';
                audioDiv.appendChild(audioElement);
            } else {
                const audioNotAvailableDiv = document.createElement('div');
                audioNotAvailableDiv.textContent = 'You have not responded to this question.';
                audioDiv.appendChild(audioNotAvailableDiv);
            }

            // Append elements to the results container
            resultsContainer.appendChild(questionDiv);
            resultsContainer.appendChild(answerDiv);
            resultsContainer.appendChild(audioDiv);

            // Make an OpenAI API call to generate an ideal answer for the current question
            generateIdealAnswer(result.question);

            // Increment the current question index for the next iteration
            currentQuestionIndex++;

        } else {
            // If there are no more questions, display a message or handle as needed
            const endMessageDiv = document.createElement('div');
            endMessageDiv.textContent = 'No more questions available.';
            resultsContainer.appendChild(endMessageDiv);

            // Change the text of the "Next Question" button to "Go Home"
            const nextQuestionButton = document.getElementById('next-question-btn');
            if (nextQuestionButton) {
                nextQuestionButton.textContent = 'Go Home';
                nextQuestionButton.removeEventListener('click', handleNextQuestion);
                nextQuestionButton.addEventListener('click', goToHome);
            } else {
                console.error('Button with ID "next-question-btn" not found');
            }
        }
    }

    // Function to handle the "Next Question" button click
    function handleNextQuestion() {
        // Call the function to fetch and display the next question with audio
        getInterviewResultsWithAudio();
    }

    // Function to handle the "Go Home" button click
    function goToHome() {
        // Redirect to the home page or perform the desired action
        window.location.href = '/home';
    }

    // Function to make an OpenAI API call to generate an ideal answer for a question
    function generateIdealAnswer(question) {
        // Make an API call to OpenAI to generate an ideal answer for the question
        // Use the response to display the ideal answer on the page
        // Example code for making the API call:
        
        fetch('/generate_ideal_answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question }),
        })
        .then(response => response.json())
        .then(data => {
            
            // Display the ideal answer on the page
            const idealAnswerDiv = document.createElement('div');
            idealAnswerDiv.className = 'ideal-answer';
            idealAnswerDiv.textContent = `Ideal Answer: ${data.idealAnswer}`;
            document.getElementById('results').appendChild(idealAnswerDiv);
        })
        .catch(error => {
            console.error('Error generating ideal answer:', error);
        });
        
        // Note: You need to implement the server endpoint ('/generate_ideal_answer') to handle this API call on the server side.
    }

    // Attach the handleNextQuestion function to the "Next Question" button
    const nextQuestionButton = document.getElementById('next-question-btn');

    if (nextQuestionButton) {
        nextQuestionButton.addEventListener('click', handleNextQuestion);
    } else {
        console.error('Button with ID "next-question-btn" not found');
    }

    // Call the function to fetch interview results with audio when the page loads
    getInterviewResultsWithAudio();
});
