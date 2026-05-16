from pypdf import PdfReader
import json
import os

STUDENT_ID = '23202058'
MEMORY_FILE = f"{STUDENT_ID}.json"



def readPdf(file_path):
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
    


def captureMemory(memoryText):
    """Tool to save content to memory when users say 'Remember'."""
    try:
        memories = readMemory()
        if memories is None:
            memories = []
        memories.append(memoryText)
        writeToMemory(memories)
        return f"✓ Remembered: {memoryText}"
    except Exception as e:
        return f"Error saving memory: {str(e)}"


def writeToMemory(data):
    """Save data to JSON memory file"""
    try:
        with open(MEMORY_FILE, mode='w', encoding='utf-8') as write_file:
            json.dump(data, write_file, indent=2)
        return True
    except Exception as e:
        print(f"Error writing to memory: {e}")
        return False


def readMemory():
    """Read memories from JSON file if it exists"""
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        return []
    except Exception as e:
        print(f"Error reading memory: {e}")
        return []

def getMemoriesContext():
    """Format memories for including in chat context"""
    memories = readMemory()
    if memories:
        return "User's memories:\n" + "\n".join([f"- {m}" for m in memories])
    return ""
    """Format memories for including in chat context"""
    memories = readMemory()
    if memories:
        return "User's memories:\n" + "\n".join([f"- {m}" for m in memories])
    return ""
       



