"""
Dropbox Integration for Health-Assistant
Provides secure file upload and download functionality using Dropbox API v2.
"""
import os
import io
import logging
from typing import Optional, Tuple
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import dropbox
from dropbox.exceptions import AuthError, ApiError
from PyPDF2 import PdfReader

# Load environment variables from the root .env file
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

# Configure logging
logger = logging.getLogger(__name__)


class DropboxClient:
    """Singleton Dropbox client for secure file operations."""
    
    _instance = None
    _dbx = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._dbx is None:
            self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Dropbox client with access token."""
        dropbox_token = os.getenv("DROPBOX_ACCESS_TOKEN")
        
        if not dropbox_token:
            logger.warning("DROPBOX_ACCESS_TOKEN not found. Dropbox features will be disabled.")
            self._dbx = None
            return
        
        try:
            self._dbx = dropbox.Dropbox(dropbox_token)
            # Test connection
            account = self._dbx.users_get_current_account()
            logger.info(f"Dropbox connected successfully for user: {account.name.display_name}")
        except AuthError as e:
            logger.error(f"Dropbox authentication failed: {str(e)}")
            self._dbx = None
        except Exception as e:
            logger.error(f"Failed to initialize Dropbox: {str(e)}")
            self._dbx = None
    
    @property
    def client(self) -> Optional[dropbox.Dropbox]:
        """Get the Dropbox client instance."""
        return self._dbx
    
    def is_connected(self) -> bool:
        """Check if Dropbox is properly connected."""
        return self._dbx is not None


# Global Dropbox client instance
_dropbox_client = DropboxClient()


def get_dropbox_client() -> Optional[dropbox.Dropbox]:
    """Get the Dropbox client instance."""
    return _dropbox_client.client


def is_dropbox_available() -> bool:
    """Check if Dropbox is available for use."""
    return _dropbox_client.is_connected()


async def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """
    Extract text content from PDF file bytes.
    
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
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


async def upload_and_read_pdf(file) -> str:
    """
    Upload a PDF to Dropbox and extract its text content.
    
    This function:
    1. Reads the uploaded file content
    2. Optionally uploads to Dropbox (if configured)
    3. Extracts text from the PDF
    
    Args:
        file: FastAPI UploadFile object
        
    Returns:
        Extracted text from the PDF
    """
    try:
        # Read file content
        contents = await file.read()
        
        if not contents or len(contents) == 0:
            raise ValueError("Uploaded file is empty")
        
        logger.info(f"Received file: {file.filename} ({len(contents)} bytes)")
        
        # Upload to Dropbox if available
        if is_dropbox_available():
            try:
                dbx = get_dropbox_client()
                # Create a unique path with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_filename = file.filename.replace(" ", "_").lower()
                dropbox_path = f"/health_records/{timestamp}_{safe_filename}"
                
                dbx.files_upload(
                    contents,
                    dropbox_path,
                    mode=dropbox.files.WriteMode("add")
                )
                logger.info(f"File uploaded to Dropbox: {dropbox_path}")
            except Exception as upload_error:
                logger.warning(f"Dropbox upload failed, continuing with text extraction: {str(upload_error)}")
        else:
            logger.info("Dropbox not configured, skipping upload")
        
        # Extract text from PDF
        text = await extract_text_from_pdf_bytes(contents)
        
        if not text or len(text.strip()) == 0:
            logger.warning("No text could be extracted from the PDF")
            return ""
        
        logger.info(f"Successfully extracted {len(text)} characters from PDF")
        return text
        
    except Exception as e:
        error_msg = f"Error processing PDF: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return f"Error: {error_msg}"


async def upload_file_to_dropbox(file_bytes: bytes, filename: str, folder: str = "health_records") -> Optional[str]:
    """
    Upload a file to Dropbox.
    
    Args:
        file_bytes: Raw bytes of the file
        filename: Name of the file
        folder: Destination folder in Dropbox
        
    Returns:
        Dropbox path if successful, None otherwise
    """
    if not is_dropbox_available():
        logger.warning("Dropbox not available")
        return None
    
    try:
        dbx = get_dropbox_client()
        
        # Create unique path with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = filename.replace(" ", "_").lower()
        dropbox_path = f"/{folder}/{timestamp}_{safe_filename}"
        
        # Ensure folder exists
        try:
            dbx.files_get_metadata(f"/{folder}")
        except ApiError:
            dbx.files_create_folder_v2(f"/{folder}")
        
        # Upload file
        dbx.files_upload(
            file_bytes,
            dropbox_path,
            mode=dropbox.files.WriteMode("add")
        )
        
        logger.info(f"File uploaded successfully: {dropbox_path}")
        return dropbox_path
        
    except Exception as e:
        logger.error(f"Failed to upload to Dropbox: {str(e)}")
        return None


async def download_file_from_dropbox(dropbox_path: str) -> Optional[bytes]:
    """
    Download a file from Dropbox.
    
    Args:
        dropbox_path: Path to the file in Dropbox
        
    Returns:
        File bytes if successful, None otherwise
    """
    if not is_dropbox_available():
        logger.warning("Dropbox not available")
        return None
    
    try:
        dbx = get_dropbox_client()
        
        # Download file
        result, response = dbx.files_download(path=dropbox_path)
        
        logger.info(f"File downloaded successfully: {dropbox_path}")
        return response.content
        
    except Exception as e:
        logger.error(f"Failed to download from Dropbox: {str(e)}")
        return None


async def list_health_records() -> list:
    """
    List all health records stored in Dropbox.
    
    Returns:
        List of file metadata dictionaries
    """
    if not is_dropbox_available():
        logger.warning("Dropbox not available")
        return []
    
    try:
        dbx = get_dropbox_client()
        
        # List files in health_records folder
        result = dbx.files_list_folder("/health_records")
        
        files = []
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                files.append({
                    "name": entry.name,
                    "path": entry.path_display,
                    "size": entry.size,
                    "modified": entry.server_modified.isoformat() if entry.server_modified else None
                })
        
        logger.info(f"Found {len(files)} health records in Dropbox")
        return files
        
    except Exception as e:
        logger.error(f"Failed to list health records: {str(e)}")
        return []
