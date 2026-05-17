from pypdf import PdfReader
from config_manager import add_memory, get_memories
from ddgs import DDGS
import wikipediaapi

def readPdf(file_path:str) -> str:
    """Reads a PDF file and returns the text content"""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page_num, page in enumerate(reader.pages):
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"
    
def web_search(query: str) -> str:
    """Search the web and return a summary of top results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))

        if not results:
            return f"No results found for: {query}"

        parts = []
        for i, result in enumerate(results, 1):
            parts.append(
                f"[{i}] {result.get('title', 'No title')}\n"
                f"    {result.get('body', 'No summary')}\n"
                f"    Source: {result.get('href', 'No URL')}"
            )

        return "\n\n".join(parts)
    except Exception as e:
        return f"Search error: {str(e)}"


def wikipedia_lookup(topic: str) -> str:
    """Fetch the summary of a Wikipedia article."""
    try:
        wiki = wikipediaapi.Wikipedia(
            user_agent="AgentLab/1.0 (educational)",
            language="en"
        )
        page = wiki.page(topic)
        if not page.exists():
            return f"Wikipedia article not found for: {topic}"
        return f"Wikipedia - {page.title}:\n{page.summary[:1500]}"
    except Exception as e:
        return f"Wikipedia error: {str(e)}"

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
                    },
                    'max_results': {
                        'type': 'integer',
                        'description': 'Maximum number of results to return'
                    }
                },
                'required': ['query']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'wikipedia_lookup',
            'description': 'Look up a topic on Wikipedia and return a summary',
            'parameters': {
                'type': 'object',
                'properties': {
                    'topic': {
                        'type': 'string',
                        'description': 'The Wikipedia article title to look up'
                    }
                },
                'required': ['topic']
            }
        }
    }
]

TOOL_FUNCTIONS = {
    'web_search': web_search,
    'wikipedia_lookup': wikipedia_lookup
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
