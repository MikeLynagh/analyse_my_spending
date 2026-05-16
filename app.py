from flask import Flask, render_template, session, jsonify, request
from flask_session import Session
import requests
import datetime
import os
from werkzeug.utils import secure_filename
from add_tool import readPdf

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

@app.route('/')
def home():
    session.clear()
    return render_template('index.html')

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files allowed'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Extract PDF content
    try:
        pdf_content = readPdf(filepath)
        session['current_pdf'] = filepath
        session['pdf_content'] = pdf_content
        session.modified = True
        return jsonify({'filename': filename, 'content': pdf_content[:500] + '...' if len(pdf_content) > 500 else pdf_content})
    except Exception as e:
        return jsonify({'error': f'Failed to read PDF: {str(e)}'}), 400

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form['text']
    
    try: 
        ollama_model = 'qwen2.5:3b'
        ollama_api_url = 'http://localhost:11434/api/chat'

        if 'history' not in session:
            session['history'] = [{'role': 'system', 'content': f'Today is {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}! Always think before you answer.'}]

        # Check if user wants to remember something
        if 'remember' in user_input.lower():
            import re
            match = re.search(r'remember\s+(.+?)(?:\.|$)', user_input, re.IGNORECASE)
            if match:
                memory_to_save = match.group(1).strip()
                from add_tool import captureMemory
                memory_response = captureMemory(memory_to_save)
                add_to_session_history('user', user_input)
                add_to_session_history('assistant', memory_response)
                return jsonify({'response': memory_response})
        
        # Add memories context to user message if they exist
        from add_tool import getMemoriesContext
        memories_context = getMemoriesContext()
        message_with_context = user_input
        if memories_context:
            message_with_context = f"{memories_context}\n\nUser: {user_input}"
        
        # If PDF is loaded, add it to the message for context
        if 'pdf_content' in session:
            message_with_context += f"\n\n[PDF Document]:\n{session['pdf_content']}"
        
        add_to_session_history('user', message_with_context)
        
        payload = {
            'model': ollama_model,
            'stream': False,
            'messages': session['history']
        }
        
        response = requests.post(ollama_api_url, json=payload, timeout=60)
        response.raise_for_status()

        ollama_data = response.json()
        model_response = ollama_data['message']['content']

        add_to_session_history('assistant', model_response)

        return jsonify({'response':model_response}
        )
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama API: {e}")
        return jsonify(
            {'error': 'failed to connect to Ollama server'}
        ), 500
    except Exception as e:
        print(f'an unexpected error occurred: {e}')
        return jsonify(
            {'error': 'unexpected error'}
        )


    
def add_to_session_history(role, content):
    if 'history' not in session:
        session['history'] = [{'role': 'system', 'content': f'Today is {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}! Give a fast response.'}]
    session['history'].append({'role': role, 'content': content})
    session.modified = True


if __name__ == '__main__':
    app.run(debug=True)