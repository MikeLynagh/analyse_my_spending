from flask import Flask, render_template, session, jsonify, request
from flask_session import Session
import datetime
import os
from werkzeug.utils import secure_filename
from add_tool import readPdf, captureMemory, getMemoriesContext, TOOLS, TOOL_FUNCTIONS
from config_manager import init_config, add_to_history, get_memories, append_summary
from ollama import chat
import re

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

init_config()

@app.route('/')
def home():
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
        if 'history' not in session:
            session['history'] = [
                {'role': 'system', 
                'content': """You are a helpful assistant with access to web search.

        -IMPORTANT: For ANY query about:
        - Current events, news, elections, politicians
        - Recent information or updates  
        - Real-time data or statistics
        - "Who is", "What is happening", "Current"
        - Location-based current information (like Galway by-election)

        YOU MUST use the web_search tool to get accurate, up-to-date information.

        Do not guess or provide old information - always search first for current topics."""}]

        # Check if user wants to remember something
        if 'remember' in user_input.lower():
            match = re.search(r'remember\s+(.+?)(?:\.|$)', user_input, re.IGNORECASE)
            if match:
                memory_text = match.group(1).strip()
                response = captureMemory(memory_text)
                add_to_session_history('user', user_input)
                add_to_session_history('assistant', response)
                add_to_history(user_input, 'qwen3.5:4b', response)
                append_summary(user_input, response)
                return jsonify({'response': response})
        
        memories = get_memories()
        message = user_input
        if memories:
            memories_text = "User's memories:\n" + "\n".join([f"- {m}" for m in memories])
            message = f"{memories_text}\n\nUser: {user_input}"

        if 'do a web search' in user_input.lower():
            search_result = TOOL_FUNCTIONS['web_search'](query=user_input)
            message += f"\n\n[Web Search Results]:\n{search_result}"
        
        if 'pdf_content' in session:
            message += f"\n\n[PDF Document]:\n{session['pdf_content']}"
        
        add_to_session_history('user', message)

        messages = session['history']
        model_responses = []

        for i in range(3):
            response = chat(
                model="qwen3.5:4b",
                messages=messages,
                tools=TOOLS
            )

            print(f"[Response] Tool calls found: {len(response.message.tool_calls) if response.message.tool_calls else 0}")

            messages.append(response.message)
            model_responses.append(response.message.content or '')

            if response.message.tool_calls:
                for tool_call in response.message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = tool_call.function.arguments
                    print(f"[TOOL CALLED] {tool_name} with args: {tool_args}")

                    if tool_name in TOOL_FUNCTIONS:
                        result = TOOL_FUNCTIONS[tool_name](**tool_args)
                        print(f"[TOOL RESULT] {str(result)[:300]}")
                        messages.append({
                            'role': 'tool',
                            'content': str(result)[:2000],
                            'tool_name': tool_name
                        })
            else:
                break
                        
        final_response = "\n".join(filter(None, model_responses))

        add_to_session_history('assistant', final_response)
        
        # Log to persistent history
        add_to_history(user_input, 'qwen3.5:4b', final_response)
        append_summary(user_input, final_response)
        session.modified = True

        return jsonify({'response': final_response})
    
    except Exception as e:
        print(f'an unexpected error occurred: {e}')
        return jsonify(
            {'error': 'unexpected error'}
        )


    
def add_to_session_history(role, content):
    if 'history' not in session:
        session['history'] = []
    session['history'].append({'role': role, 'content': content})
    session.modified = True


if __name__ == '__main__':
    app.run(debug=True)
