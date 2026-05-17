# Agentic Chat Application with Multimodal Support

Flask web application for a college assignment. It provides a simple chat UI, persistent user memory, PDF upload support, conversation history logging, and an Ollama-backed AI assistant using `qwen3.5:4b`.

Student ID: `23202058`  
Name: `Michael Lynagh`

## Features

- Web-based chat interface
- Text chat
- PDF upload and text extraction
- Persistent memories saved to `user_config/23202058.json`
- Full conversation history saved to `user_config/23202058_history.json`
- Web search tool available to the model
- Ollama integration with `qwen3.5:4b`

## Project Structure

- `app.py` - main Flask application and routes
- `add_tool.py` - PDF reader, web search, and memory helper functions
- `config_manager.py` - persistent config and history management
- `templates/index.html` - chat user interface
- `user_config/` - saved user config and history files
- `uploads/` - uploaded PDF files

## Data Files

### `user_config/23202058.json`

Stores:
- `user_id`
- `name`
- `memories`
- `summary`
- `updated`

If the file does not exist, it is created automatically on startup.

### `user_config/23202058_history.json`

Stores a complete conversation history with one appended entry per user prompt:
- `datetime`
- `user_id`
- `prompt`
- `agent`
- `reply`

## Requirements

- Python 3.8+
- Ollama installed locally
- Ollama running before starting the Flask app
- `qwen3.5:4b` pulled in Ollama

## Installation

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Ollama Setup

Start Ollama and pull the model:

```bash
ollama pull qwen3.5:4b
ollama serve
```

## Run the Application

With the virtual environment active:

```bash
python app.py
```

Then open:

`http://127.0.0.1:5000`

## How It Works

1. On startup, the app creates `user_config/23202058.json` and `user_config/23202058_history.json` if they do not already exist.
2. The user opens the web chat UI in the browser.
3. The user can send a normal text message or upload a PDF.
4. If the user says `remember ...`, the text is added to the `memories` list in the config file.
5. Saved memories and uploaded PDF text are added to the conversation context.
6. The assistant can use its `web_search` tool when needed.
7. Each conversation turn is logged to the history file and a rolling summary is stored in the user config file.

## Notes

- The app assumes the authenticated user is already known and uses student ID `23202058`.
- PDF support is implemented as the second modality.
- If Ollama is not running, chat requests will fail until it is started.
- `templates/upload_form.html` is an older unused template and is not part of the main UI flow.
