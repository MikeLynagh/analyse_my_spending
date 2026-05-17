import json
import os
from datetime import datetime

USER_ID = "23202058"
USER_NAME = "Michael"
CONFIG_DIR = "user_config"
USER_CONFIG_FILE = os.path.join(CONFIG_DIR, f"{USER_ID}.json")
HISTORY_FILE = os.path.join(CONFIG_DIR, f"{USER_ID}_history.json")


def init_config():
    """Initialize config directory and files on startup"""
    # Create directory if doesn't exist
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    
    # Initialize user config if doesn't exist
    if not os.path.exists(USER_CONFIG_FILE):
        user_config = {
            "user_id": USER_ID,
            "name": USER_NAME,
            "memories": [],
            "summary": "Conversation started",
            "updated": datetime.now().isoformat()
        }
        save_user_config(user_config)
    
    # Initialize history file if doesn't exist
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f, indent=2)


def load_user_config():
    """Load user configuration from JSON"""
    try:
        if os.path.exists(USER_CONFIG_FILE):
            with open(USER_CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading user config: {e}")
    return None


def save_user_config(config):
    """Save user configuration to JSON"""
    try:
        config['updated'] = datetime.now().isoformat()
        with open(USER_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving user config: {e}")


def add_to_history(prompt, agent, reply):
    """Append conversation entry to history file"""
    try:
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        
        entry = {
            "datetime": datetime.now().isoformat(),
            "user_id": USER_ID,
            "prompt": prompt,
            "agent": agent,
            "reply": reply
        }
        history.append(entry)
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error saving to history: {e}")


def add_memory(memory_text):
    """Add memory to user config"""
    try:
        config = load_user_config()
        if config:
            if memory_text not in config['memories']:
                config['memories'].append(memory_text)
                save_user_config(config)
                return True
    except Exception as e:
        print(f"Error adding memory: {e}")
    return False


def get_memories():
    """Get all memories from user config"""
    try:
        config = load_user_config()
        if config:
            return config['memories']
    except Exception as e:
        print(f"Error getting memories: {e}")
    return []


def update_summary(summary_text):
    """Update conversation summary in config"""
    try:
        config = load_user_config()
        if config:
            config['summary'] = summary_text
            save_user_config(config)
    except Exception as e:
        print(f"Error updating summary: {e}")


def append_summary(prompt, reply, max_length=1200):
    """Append a short rolling conversation summary to user config."""
    try:
        config = load_user_config()
        if config:
            entry = f"User: {prompt} | Assistant: {reply}"
            current = config.get('summary', '')
            combined = entry if not current or current == "Conversation started" else f"{current}\n{entry}"
            config['summary'] = combined[-max_length:]
            save_user_config(config)
    except Exception as e:
        print(f"Error appending summary: {e}")
