"""
Health-Assistant FastAPI Backend
Provides endpoints for health queries and medical document analysis.
"""
import os
import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Load environment variables from the root .env file
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Initialize FastAPI app
app = FastAPI(
    title="Health-Assistant API",
    description="API for health-related queries and medical document analysis using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://localhost:8502",
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8502",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Pydantic Models ====================

class HealthAdviceRequest(BaseModel):
    """Request model for health advice endpoint."""
    query: str = Field(..., min_length=1, max_length=5000, description="User's health query")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the symptoms of diabetes?"
            }
        }


class HealthAdviceResponse(BaseModel):
    """Response model for health advice endpoint."""
    status: str = Field(..., description="Status of the request (success/error)")
    response: Optional[str] = Field(None, description="AI-generated health advice")
    message: Optional[str] = Field(None, description="Error message if status is error")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "response": "Diabetes symptoms include frequent urination, increased thirst...",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class ChatMessage(BaseModel):
    """Model for a single chat message."""
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatHistory(BaseModel):
    """Model for chat history."""
    messages: List[ChatMessage] = Field(default_factory=list)


class HealthCheck(BaseModel):
    """Health check response model."""
    status: str
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ==================== Endpoints ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Health-Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Health check endpoint to verify API is running."""
    return HealthCheck(
        status="healthy",
        service="health-assistant-api",
        version="1.0.0"
    )


@app.post("/api/chat", response_model=HealthAdviceResponse, tags=["Chat"])
async def chat_endpoint(request: HealthAdviceRequest):
    """
    Chat endpoint for health queries without file upload.
    
    This endpoint accepts a text query and returns AI-generated health advice.
    """
    try:
        logger.info(f"Received chat query: {request.query[:100]}...")
        
        # Import here to avoid circular imports
        from app.agents.gemini_tool import get_health_advice
        
        response = await get_health_advice(query=request.query, file_text=None)
        
        if not response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate response from AI model"
            )
        
        logger.info("Successfully generated health advice")
        return HealthAdviceResponse(
            status="success",
            response=response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return HealthAdviceResponse(
            status="error",
            message=f"Error processing request: {str(e)}"
        )


@app.post("/api/upload", response_model=HealthAdviceResponse, tags=["Upload"])
async def upload_and_analyze_endpoint(
    query: str = Form(..., min_length=1, max_length=5000),
    file: UploadFile = File(...)
):
    """
    Upload a medical document (PDF) and get AI analysis.
    
    Accepts a health query along with a PDF file containing medical records.
    The AI will analyze both the query and the document to provide personalized advice.
    """
    try:
        logger.info(f"Received upload request - Query: {query[:100]}..., File: {file.filename}")
        
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )
        
        # Validate file size (max 10MB)
        file_size = 0
        contents = await file.read()
        file_size = len(contents)
        max_size = 10 * 1024 * 1024  # 10MB
        
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum limit of 10MB. Current size: {file_size / 1024 / 1024:.2f}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty"
            )
        
        logger.info(f"File validated - Size: {file_size / 1024:.2f}KB")
        
        # Extract text from PDF
        from app.utils.helpers import extract_text_from_pdf
        
        try:
            extracted_text = extract_text_from_pdf(contents, use_plumber=True)
        except Exception as pdf_error:
            logger.warning(f"pdfplumber failed, trying PyPDF2: {str(pdf_error)}")
            extracted_text = extract_text_from_pdf(contents, use_plumber=False)
        
        if not extracted_text or len(extracted_text.strip()) == 0:
            logger.warning("No text could be extracted from the PDF")
            extracted_text = None
        else:
            logger.info(f"Extracted {len(extracted_text)} characters from PDF")
        
        # Get AI response
        from app.agents.gemini_tool import get_health_advice
        
        response = await get_health_advice(query=query, file_text=extracted_text)
        
        if not response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate response from AI model"
            )
        
        logger.info("Successfully analyzed document and generated advice")
        return HealthAdviceResponse(
            status="success",
            response=response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload endpoint: {str(e)}", exc_info=True)
        return HealthAdviceResponse(
            status="error",
            message=f"Error processing upload: {str(e)}"
        )


@app.post("/api/health-advice", response_model=HealthAdviceResponse, tags=["Legacy"])
async def get_health_advice_endpoint(
    query: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    """
    Legacy endpoint for backward compatibility.
    Handles both chat-only and file upload scenarios.
    """
    try:
        logger.info(f"Received legacy request - Query: {query[:100]}...")
        
        extracted_text = None
        
        # Process file if uploaded
        if file and file.filename:
            logger.info(f"Processing file: {file.filename}")
            
            if not file.filename.lower().endswith('.pdf'):
                logger.warning(f"Unsupported file type: {file.filename}")
                return HealthAdviceResponse(
                    status="error",
                    message="Only PDF files are supported"
                )
            
            contents = await file.read()
            
            from app.utils.helpers import extract_text_from_pdf
            
            try:
                extracted_text = extract_text_from_pdf(contents, use_plumber=True)
            except Exception as pdf_error:
                logger.warning(f"pdfplumber failed, trying PyPDF2: {str(pdf_error)}")
                extracted_text = extract_text_from_pdf(contents, use_plumber=False)
            
            if extracted_text:
                logger.info(f"Extracted {len(extracted_text)} characters from PDF")
        
        # Get AI response
        from app.agents.gemini_tool import get_health_advice
        
        response = await get_health_advice(query=query, file_text=extracted_text)
        
        return HealthAdviceResponse(
            status="success" if response else "error",
            response=response if response else "No response generated",
            message=None if response else "Empty response from AI model"
        )
        
    except Exception as e:
        logger.error(f"Error in legacy endpoint: {str(e)}", exc_info=True)
        return HealthAdviceResponse(
            status="error",
            message=f"Error: {str(e)}"
        )


# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": f"Internal server error: {str(exc)}",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
