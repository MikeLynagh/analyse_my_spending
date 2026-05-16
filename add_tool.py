from pypdf import PdfReader
from config_manager import add_memory, get_memories
import requests
import re
from ollama import chat

def readPdf(file_path:str) -> str:
    """Reads a PDF file and returns the text content"""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page_num, page in enumerate(reader.pages):
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"
    
def web_search(query: str) -> str:
    """Search the web using DuckDuckGo (no api needed)"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        result = f"Search: '{query}'\n"
        if data.get('AbstractText'):
            result += f"Summary: {data['AbstractText']}\n"
        if data.get('RelatedTopics'):
            result += "Topics:\n"
            for i, topic in enumerate(data['RelatedTopics'][:3], 1):
                if topic.get('Text'):
                    result += f"{i}. {topic['Text']}\n"

        return result if len(result) > 30 else 'No results found'
    except Exception as e:
        return f"Search error: {str(e)}"

TOOLS = [
   {
        'type': 'function',
        'function': {
            'name': 'web_search',
            'description': 'Search the web for information',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'The search query'
                    }
                },
                'required': ['query']
            }
        }
    }
]

TOOL_FUNCTIONS = {
    'web_search': web_search
}


def captureMemory(memoryText):
    """Tool to save content to memory when users say 'Remember'."""
    try:
        success = add_memory(memoryText)
        if success:
            return f"✓ Remembered: {memoryText}"
        else:
            return f"Memory already exists: {memoryText}"
    except Exception as e:
        return f"Error saving memory: {str(e)}"


def getMemoriesContext():
    """Format memories for including in chat context"""
    memories = get_memories()
    if memories:
        return "User's memories:\n" + "\n".join([f"- {m}" for m in memories])
    return ""
       



