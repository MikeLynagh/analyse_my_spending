from pypdf import PdfReader

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