from flask import Flask, render_template, redirect, send_file, session, url_for, request,jsonify
import speech_recognition as sr
import os
import sqlite3
import openai
import bcrypt
import base64
import requests



# Set your OpenAI API key
openai.api_key = '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'
api_key='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'
app = Flask(__name__, static_folder="statics")
app.secret_key = os.urandom(24)



# Create a SQLite database and a table to store form data
def create_database():
    try:
        # Connect to the SQLite database
        with sqlite3.connect('form-data.db') as conn:
            c = conn.cursor()

            # Drop existing table (for testing purposes)
            c.execute('DROP TABLE IF EXISTS InterviewData')

            # Create table
            c.execute('''
                CREATE TABLE IF NOT EXISTS InterviewData (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jobDescription TEXT,
                    jobRole TEXT,
                    experience TEXT,
                    skills TEXT
                )
            ''')

            # Drop existing InterviewQuestions table (for testing purposes)
            c.execute('DROP TABLE IF EXISTS InterviewQuestions')

            # Create InterviewQuestions table
            c.execute('''
                CREATE TABLE IF NOT EXISTS InterviewQuestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT,
                    answer TEXT
                )
            ''')
            c.execute('''DROP TABLE IF EXISTS Users''')
            c.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUW NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
            ''')
            conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False

def dropTable():
    with sqlite3.connect('form-data.db') as conn:
            c = conn.cursor()
            c.execute('DROP TABLE IF EXISTS InterviewData')
            c.execute('DROP TABLE IF EXISTS InterviewQuestions')


# Generate interview-questions
def generate_interview_questions(input_data):
    try:
        # Call OpenAI API to generate questions based on the input data
        response = openai.Completion.create(
            engine="text-davinci-003",  # or another available engine
            prompt=f"Generate 1  short interview question for a candidate with the following information, that can be answered with in 30 seconds:\n{input_data}\n",
            max_tokens=150,
            n=10,  # Number of questions to generate
            stop=None,  # Custom stop sequence to end the generated questions
        )

        # Extract top 10 questions and answers from the API response
        questions = [item['text'] for item in response['choices']]
        answers = []  # You might want to handle answers differently based on your use case
        
        return questions, answers

    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        # Handle the error, you might want to log it or return a default set of questions and answers
        return [], []

    except Exception as e:
        print(f"Unexpected error: {e}")
        # Handle other unexpected errors
        return [], []



#saving the audio
audio_no=0
@app.route('/process_audio', methods=['POST'])
def process_audio():
    global audio_no
    try:
        # Check if the request contains files
        if 'audio' in request.files:
            audio_file = request.files['audio']

            # Retrieve the question index from the form data
            

            # Save the audio file with the question number as the filename
            audio_filename = f'recording_q{audio_no}.wav'
            audio_path = f'Audiofiles/{audio_filename}'  # Update with your desired path
            audio_file.save(audio_path)
            audio_no=audio_no+1
            # ... other processing ...

            return jsonify({'status': 'success'})

        else:
            return jsonify({'error': 'No audio file received'})

    except Exception as e:
        return jsonify({'error': str(e)})



# Define your routes
@app.route('/')
def land():
    return render_template('index.html')



@app.route('/index')
def index():
    return render_template('index.html')




@app.route('/home')
def home():
    
    user_email = session.get('user_email')
    return render_template('home.html', user_email=user_email)



# Simulate a login or signup process
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            with sqlite3.connect('form-data.db') as conn:
                conn.row_factory = sqlite3.Row  # This allows accessing columns by name
                c = conn.cursor()
                c.execute('SELECT * FROM Users WHERE email = ? AND password = ?', (email, password))
                user = c.fetchone()

            if user:
                session['user_email'] = user['email']
                print("User logged in successfully.")
                print(session)  # Add this line to check session data
                return redirect(url_for('home'))

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")

    return render_template('index.html')



@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('index'))

   
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        try:
            with sqlite3.connect('form-data.db') as conn:
                c = conn.cursor()
                c.execute('INSERT INTO Users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
                conn.commit()

            return redirect(url_for('index'))

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")

    return render_template('index.html')



@app.route('/interview.html')
def interview():
    return render_template('interview.html')



@app.route('/questions.html/<int:question_number>', methods=['GET', 'POST'])
def questions(question_number):
    if request.method == 'GET':
        interview_questions = get_interview_questions_from_database()

        if interview_questions and 1 <= question_number <= len(interview_questions):
            current_question = interview_questions[question_number - 1]
            return render_template('questions.html', current_question=current_question, current_question_index=question_number)
        else:
            return render_template('feedback.html')  # Create a template for this case

    elif request.method == 'POST':
        # Handle user's response to a question (speech, skip, timeout)
        # You can add logic to process the user's response here
        # For simplicity, let's assume the user's response is posted to this route

        # Retrieve the next question index from the request (assuming it's sent by the client)
        current_question_index_str = request.form.get('current_question_index')

        # Check if the value is a non-empty string and consists of digits before converting to an integer
        if current_question_index_str and current_question_index_str.isdigit():
            current_question_index = int(current_question_index_str)

            # Update the database or perform other actions based on the user's response
            # ...

            # Retrieve the next question from the database
            next_question = get_next_question(current_question_index)

            # If there are more questions, render the questions.html template with the next question
            if next_question:
                return render_template('questions.html', current_question=next_question, current_question_index=current_question_index + 1)
            else:
                # If all questions are answered, redirect to a thank you page or another route
                return render_template('feedback.html')
        else:
            # Handle the case where the current_question_index is not a valid integer
            return jsonify({'status': 'error', 'message': 'Invalid current_question_index'})



# Helper function to get interview questions from the database
def get_interview_questions_from_database():
    try:
        with sqlite3.connect('form-data.db') as conn:
            c = conn.cursor()
            c.execute('SELECT question FROM InterviewQuestions')
            questions = c.fetchall()

        return [question[0] for question in questions]

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return []
    
    

# Helper function to get the next available question number
def get_next_question_number():
    try:
        with sqlite3.connect('form-data.db') as conn:
            c = conn.cursor()
            c.execute('SELECT MAX(id) FROM InterviewQuestions')
            max_id = c.fetchone()[0]
            next_question_number = max_id + 1 if max_id is not None else 1

        return next_question_number

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None



# Helper function to get the next interview question based on the current index
def get_next_question(current_index):
    try:
        with sqlite3.connect('form-data.db') as conn:
            c = conn.cursor()
            c.execute('SELECT question FROM InterviewQuestions WHERE id = ?', (current_index + 1,))
            next_question = c.fetchone()

        return next_question[0] if next_question else None

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None



@app.route('/submit_application', methods=['POST'])
def submit_application():
    if request.method == 'POST':
        job_description = request.form['job_description']
        job_role = request.form['job_role']
        experience = request.form['experience']
        skills = request.form['Skills']

        try:
            # Open a connection to the database
            with sqlite3.connect('form-data.db') as conn:
                c = conn.cursor()

                # Insert form data into the database
                c.execute('''
                    INSERT INTO InterviewData (jobDescription, jobRole, experience, skills)
                    VALUES (?, ?, ?, ?)
                ''', (job_description, job_role, experience, skills))

                conn.commit()

                # Call OpenAI API to generate interview questions
                input_data = f"{job_description} {job_role} {experience} {skills}"
                questions, answers = generate_interview_questions(input_data)

                # Save generated questions and answers in another table
                for question in questions:
                    c.execute('''
                        INSERT INTO InterviewQuestions (question, answer)
                        VALUES (?, ?)
                    ''', (question, " "))
                conn.commit()
                next_question_number = get_next_question_number()

            # After successfully processing the form submission
            return jsonify({'status': 'success'})

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return jsonify({'status': 'error'})



# Route to handle the AJAX request for fetching interview results with audio
@app.route('/get_interview_results_with_audio', methods=['GET'])
def get_interview_results_with_audio_route():
    try:
        # List all audio files in the 'Audiofiles' directory
        audio_files = [f for f in os.listdir('Audiofiles') if f.startswith('recording_q')]

        # Extract question numbers from file names
        question_numbers = [int(file.split('_')[1].split('.')[0][1:]) for file in audio_files]

        # Fetch questions and answers from the database based on question numbers
        results = []
        with sqlite3.connect('form-data.db') as conn:
            c = conn.cursor()
            for q_number in question_numbers:
                c.execute('SELECT id, question, answer FROM InterviewQuestions WHERE id = ?', (q_number,))
                question_data = c.fetchone()
                if question_data:
                    question_id, question_text, answer = question_data

                    # Check if the corresponding audio file exists
                    audio_file_path = f'Audiofiles/recording_q{q_number}.wav'
                    audio_exists = os.path.isfile(audio_file_path)

                    # Include information in the result
                    results.append({
                        'question': question_text,
                        'audio_path': audio_file_path if audio_exists else None,
                        'answer': answer,
                        'audio_exists': audio_exists
                    })

        # Prepare the response data
        response_data = {'status': 'success', 'results': results}

        return jsonify(response_data)

    except Exception as e:
        print(f"Error fetching interview results with audio: {e}")
        return jsonify({'status': 'error', 'message': 'Error fetching interview results with audio'})



@app.route('/result.html', methods=['GET'])
def result_page():
    return render_template('result.html')



# Route to serve audio files
@app.route('/audio/<path:filename>', methods=['GET'])
def serve_audio(filename):
    return send_file(filename, as_attachment=True)



# Route to handle the AJAX request for viewing results
@app.route('/view_result', methods=['GET'])
def view_result():
    try:
        # Fetch interview results from the server, including audio paths
        results = get_interview_results_with_audio_route().json['results']

        # Prepare the response data
        response_data = {'status': 'success', 'results': results}

        return jsonify(response_data)

    except Exception as e:
        print(f"Error in /view_result: {str(e)}")
        return jsonify({'status': 'error', 'message': f'An error occurred while fetching interview results. Details: {str(e)}'})



# Function to generate an ideal answer for a given question using OpenAI API
def generate_ideal_answer(question):
    try:
        # Call OpenAI API to generate the ideal answer
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Provide an ideal answer to the following interview question:\n{question}\n",
            max_tokens=150,
            n=1,
            stop=None
        )

        # Extract the answer from the API response
        ideal_answer = response['choices'][0]['text']

        return ideal_answer

    except Exception as e:
        print(f"OpenAI API error: {e}")
        # Handle the error, you might want to log it or return a default ideal answer
        return f"Error generating ideal answer: {e}"



@app.route('/generate_ideal_answer', methods=['POST'])
def generate_ideal_answer_route():
    try:
        # Get the question from the request data
        data = request.get_json()
        question = data.get('question', '')

        # Generate the ideal answer using OpenAI API
        ideal_answer = generate_ideal_answer(question)

        # Return the ideal answer in the response
        response_data = {'status': 'success', 'idealAnswer': ideal_answer}
        return jsonify(response_data)

    except Exception as e:
        print(f"Error generating ideal answer: {e}")
        return jsonify({'status': 'error', 'message': 'Error generating ideal answer'})



if __name__ == '__main__':
    if create_database():
        app.run(debug=True)
    else:
        print("Failed to create the database.")
