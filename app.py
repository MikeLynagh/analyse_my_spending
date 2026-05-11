from flask import Flask, render_template, session, jsonify, request
from flask_session import Session
from bot import pritgpt, prompt


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
    response = chatbot_query(user_input)
    return jsonify({'response':response})

def chatbot_query(user_input):
    python_or_gen = prompt.python_or_general_response(user_input)
    add_to_session_history('user', user_input)
    response = qagpt_response([{}'role': 'user', 'content': python_or_gen}], model='Qwen3.5', type='ollama')
    if 'true' in response.choices[0].message.content.lower():
        print('In true case: '+response.choices[0].message.content.lower())
        code = CodeGenerator(prompt=user_input)
        gen_code - code.generate_code()
        final_response = code.debug_and_execute(gen_code)
        return final_response
    else:
        print('session history')

        return final_response
    
def add_to_session_history(role, content):
    if 'history' not in session:
        session['history'] = [{'role': 'system', 'content': f'Today is {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}! Always think before you answer.'}]
        session['hitory'].append({'role': role, 'content': content})
        session.modified = True

if __name__ == '__main__':
    app.run(debug=True)