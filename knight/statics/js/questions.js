let mediaRecorder, recordedChunks = [], recordedAudio;
let timerCount = 30;
let timerInterval;

async function startRecording() {
    try {
        // Clear the recordedChunks array when starting a new recording
        recordedChunks = [];

        // Disable buttons during recording
        document.getElementById('record-button').disabled = true;
        document.getElementById('submit-button').disabled = true;

        // Display recording indication
        document.getElementById('record-button').innerText = 'Recording...';
        timerInterval = setInterval(function () {
            document.getElementById('timer-count').innerText = timerCount;
            if (timerCount === 0) {
                clearInterval(timerInterval);
                // Don't submit here, let onresult handle it
                document.getElementById('submit-button').disabled=false;
            }
            timerCount--;
        }, 1000);

        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            // Reset the timer and enable the record button
            timerCount = 30;
            document.getElementById('record-button').disabled = false;
            document.getElementById('submit-button').disabled = false;
            document.getElementById('record-button').innerText = '🎙️ Record Again Answer';

            // Display the audio player and set the source
            if (recordedChunks.length > 0) {
                const audioBlob = new Blob(recordedChunks, { type: 'audio/wav' });
                recordedAudio = new Audio(window.URL.createObjectURL(audioBlob));
                document.getElementById('audio-player').src = recordedAudio.src;
                document.getElementById('audio-player').style.display = 'block';
            } else {
                console.error('No audio recorded.');
            }
        };

        mediaRecorder.start();

        // Record for 30 seconds (adjust as needed)
        setTimeout(() => {
            mediaRecorder.stop();
            clearInterval(timerInterval);
        }, timerCount * 1000);
    } catch (error) {
        console.error('Error accessing microphone:', error);
        // Handle the error, e.g., display an error message to the user
    }
}

function submitRecording() {
    if (recordedChunks.length > 0) {
        const audioBlob = new Blob(recordedChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        // Add the current_question_index to the form data
        const currentQuestionIndex = document.getElementById('current-question-index').value;
        formData.append('current_question_index', currentQuestionIndex);

        fetch('/process_audio', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Handle the response from the server
            console.log('Server response:', data);

            // Redirect to the next question page if the status is success
            if (data && data.status === 'success') {
                const nextQuestionIndex = parseInt(currentQuestionIndex) + 1;
                window.location.href = `/questions.html/${nextQuestionIndex}`;
            }
        })
        .catch(error => {
            console.error('Error sending audio to the server:', error);
        });
    } else {
        console.error('No audio recorded.');
    }
}



function skipQuestion() {
    clearInterval(timerInterval);

    // Add logic to skip the current question and proceed to the next one
    document.getElementById('response-form').submit();
}
