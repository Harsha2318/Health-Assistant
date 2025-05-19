import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the root .env file
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import tools
from .agents.gemini_tool import get_health_advice
from .agents.dropbox_tool import upload_and_read_pdf

@app.post("/api/health-advice")
async def get_health_advice_endpoint(
    query: str = Form(...),
    file: UploadFile = File(None)
):
    try:
        print(f"Received query: {query}")
        
        # Process file if uploaded
        file_text = None
        if file and file.filename:
            print(f"Processing file: {file.filename}")
            if file.filename.endswith('.pdf'):
                file_text = await upload_and_read_pdf(file)
                print(f"Extracted {len(file_text or '')} characters from PDF")
            else:
                print(f"Unsupported file type: {file.filename}")
        
        print("Getting health advice...")
        response = await get_health_advice(query, file_text)
        print(f"Response generated: {response[:100]}..." if response else "Empty response")
        
        return {"status": "success", "response": response}
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return {"status": "error", "message": error_msg}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
