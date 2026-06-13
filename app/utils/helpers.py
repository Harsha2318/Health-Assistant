"""
Utility functions for PDF parsing, text processing, and formatting.
"""
import io
import re
from typing import Optional, List
from PyPDF2 import PdfReader
import pdfplumber


def extract_text_from_pdf_pypdf2(file_bytes: bytes) -> str:
    """
    Extract text from a PDF using PyPDF2.
    
    Args:
        file_bytes: Raw bytes of the PDF file
        
    Returns:
        Extracted text content
    """
    try:
        pdf_reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting text with PyPDF2: {str(e)}")


def extract_text_from_pdf_plumber(file_bytes: bytes) -> str:
    """
    Extract text from a PDF using pdfplumber (better layout preservation).
    
    Args:
        file_bytes: Raw bytes of the PDF file
        
    Returns:
        Extracted text content with better formatting
    """
    try:
        text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting text with pdfplumber: {str(e)}")


def extract_text_from_pdf(file_bytes: bytes, use_plumber: bool = True) -> str:
    """
    Extract text from a PDF file using the specified method.
    
    Args:
        file_bytes: Raw bytes of the PDF file
        use_plumber: If True, use pdfplumber; otherwise use PyPDF2
        
    Returns:
        Extracted text content
    """
    if use_plumber:
        return extract_text_from_pdf_plumber(file_bytes)
    else:
        return extract_text_from_pdf_pypdf2(file_bytes)


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text.
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s.,;:!?\'\"()-]', '', text)
    
    # Normalize line breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()


def chunk_text(text: str, max_chunk_size: int = 4000, overlap: int = 200) -> List[str]:
    """
    Split text into chunks for processing with LLM token limits.
    
    Args:
        text: Text to chunk
        max_chunk_size: Maximum characters per chunk
        overlap: Number of overlapping characters between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_chunk_size
        
        # Try to break at a sentence boundary
        if end < len(text):
            # Look for sentence endings in the overlap region
            for sep in ['. ', '! ', '? ', '\n\n']:
                last_sep = text[start:end].rfind(sep)
                if last_sep > max_chunk_size // 2:
                    end = start + last_sep + len(sep)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
    
    return chunks


def format_medical_context(query: str, extracted_text: Optional[str] = None) -> str:
    """
    Format the user query with medical context from extracted documents.
    
    Args:
        query: User's health query
        extracted_text: Optional text extracted from medical documents
        
    Returns:
        Formatted prompt for the AI model
    """
    base_prompt = """You are a helpful, empathetic, and knowledgeable healthcare assistant. 
Your role is to provide accurate, easy-to-understand health information while being compassionate.

IMPORTANT GUIDELINES:
1. Always prioritize patient safety - if symptoms suggest a medical emergency, advise seeking immediate professional help.
2. Provide evidence-based information but clearly state when something requires professional medical evaluation.
3. Use clear, non-technical language when possible, explaining medical terms when necessary.
4. Be supportive and understanding, acknowledging the user's concerns.
5. Never diagnose conditions definitively - instead, explain possibilities and recommend appropriate next steps.
6. Respect privacy and handle all health information sensitively.

"""
    
    if extracted_text:
        base_prompt += f"""
RELEVANT MEDICAL INFORMATION FROM USER'S DOCUMENTS:
{extracted_text}

USER'S QUESTION:
{query}

Please analyze the medical information provided above and answer the user's question thoughtfully, 
referencing specific details from their documents where relevant.
"""
    else:
        base_prompt += f"""
USER'S QUESTION:
{query}

Please provide a helpful and informative response based on your medical knowledge.
"""
    
    return base_prompt


def validate_file_type(filename: str, allowed_types: List[str] = None) -> bool:
    """
    Validate if the file type is allowed.
    
    Args:
        filename: Name of the file
        allowed_types: List of allowed extensions (default: ['pdf'])
        
    Returns:
        True if valid, False otherwise
    """
    if allowed_types is None:
        allowed_types = ['pdf']
    
    if not filename or '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed_types


def truncate_text(text: str, max_length: int = 10000) -> str:
    """
    Truncate text to a maximum length while preserving完整性.
    
    Args:
        text: Text to truncate
        max_length: Maximum character count
        
    Returns:
        Truncated text with indicator if truncated
    """
    if not text or len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    # Try to end at a sentence boundary
    for sep in ['. ', '! ', '? ', '\n']:
        last_sep = truncated.rfind(sep)
        if last_sep > max_length // 2:
            truncated = truncated[:last_sep + len(sep)]
            break
    
    return truncated + "\n\n[Content truncated due to length...]"
