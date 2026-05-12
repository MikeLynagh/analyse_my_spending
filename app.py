from flask import Flask, render_template, session, jsonify, request
from flask_session import Session
import requests


import datetime

app = Flask(__name__)

app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

@app.route('/')
def home():
    session.clear()
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form['text']

    
    try: 
        ollama_model = 'qwen2.5:3b'
        ollama_api_url = 'http://localhost:11434/api/chat'

        if 'history' not in session:
            session['history'] = [{'role': 'system', 'content': f'Today is {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}! Always think before you answer.'}]

        add_to_session_history('user', user_input)
 
        
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