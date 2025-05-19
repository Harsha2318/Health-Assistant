import os
import dropbox
from dropbox.exceptions import AuthError
import io
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from the root .env file
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

# Initialize Dropbox client
try:
    DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
    if not DROPBOX_ACCESS_TOKEN:
        raise ValueError("DROPBOX_ACCESS_TOKEN not found in environment variables. Please check your .env file in the project root.")
    
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    # Test the connection
    dbx.users_get_current_account()
except Exception as e:
    print(f"Error initializing Dropbox: {str(e)}")
    dbx = None

async def upload_and_read_pdf(file) -> str:
    """
    Upload a PDF to Dropbox and extract its text content.
    
    Args:
        file: FastAPI UploadFile object
        
    Returns:
        str: Extracted text from the PDF
    """
    if not dbx:
        return "Error: Dropbox not properly configured."
    
    try:
        # Read file content
        contents = await file.read()
        
        # Upload to Dropbox
        file_path = f"/health_records/{file.filename}"
        dbx.files_upload(
            contents,
            file_path,
            mode=dropbox.files.WriteMode("overwrite")
        )
        
        # Extract text from PDF
        pdf = PdfReader(io.BytesIO(contents))
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
            
        return text
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return f"Error processing PDF: {str(e)}"
