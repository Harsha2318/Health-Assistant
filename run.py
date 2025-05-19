import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the root .env file
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(env_path)

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent))

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
