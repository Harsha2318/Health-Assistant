"""
Health-Assistant Streamlit Frontend
A modern chat interface for health queries with PDF upload support.
"""
import streamlit as st
import base64
import os
import sys
import requests
import time
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from the root .env file
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Get backend URL from environment or use default
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Set page config - MUST be the first Streamlit command
st.set_page_config(
    page_title="HealthCare Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better chat interface
st.markdown("""
<style>
    /* Main background */
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Chat message styling */
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        max-width: 85%;
        line-height: 1.5;
    }
    
    /* User message */
    [data-testid="stChatMessage"][data-message-author-role="user"] {
        background-color: #2b5278;
        margin-left: auto;
        border-bottom-right-radius: 0.2rem;
    }
    
    /* Assistant message */
    [data-testid="stChatMessage"][data-message-author-role="assistant"] {
        background-color: #1e1e1e;
        border: 1px solid #333;
        border-bottom-left-radius: 0.2rem;
    }
    
    /* Message content */
    .stChatMessage p {
        margin: 0.2rem 0;
        color: #ffffff;
    }
    
    /* Lists */
    .stChatMessage ul, .stChatMessage ol {
        margin: 0.5rem 0 0.5rem 1.5rem;
        padding-left: 0.5rem;
    }
    
    .stChatMessage li {
        margin: 0.5rem 0;
        color: #e0e0e0;
    }
    
    /* Headers and bold text */
    .stChatMessage h1, 
    .stChatMessage h2, 
    .stChatMessage h3, 
    .stChatMessage h4, 
    .stChatMessage h5, 
    .stChatMessage h6 {
        color: #4c9aff;
        margin: 0.8rem 0 0.5rem 0;
    }
    
    .stChatMessage strong {
        color: #4c9aff;
    }
    
    /* Code blocks */
    .stChatMessage code {
        background-color: #2a2a2a;
        color: #f0f0f0;
        padding: 0.2rem 0.4rem;
        border-radius: 0.3rem;
        font-family: 'Courier New', monospace;
    }
    
    /* Links */
    .stChatMessage a {
        color: #4c9aff;
        text-decoration: none;
    }
    
    .stChatMessage a:hover {
        text-decoration: underline;
    }
    
    /* Input field */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        background-color: #333333;
        color: #ffffff;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
    }
    
    /* File uploader */
    .file-uploader {
        border: 2px dashed #4CAF50;
        border-radius: 5px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1a1a1a;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError {
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def check_backend_health() -> bool:
    """Check if the backend API is healthy."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def send_chat_message(query: str) -> tuple[bool, str]:
    """
    Send a chat message to the backend API.
    
    Args:
        query: User's health query
        
    Returns:
        Tuple of (success, response_or_error)
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json={"query": query},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                return True, result.get("response", "No response content")
            else:
                return False, result.get("message", "Unknown error")
        else:
            return False, f"Server error (Status {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to the backend server. Please ensure it's running."
    except requests.exceptions.Timeout:
        return False, "Request timed out. Please try again."
    except Exception as e:
        return False, f"Error: {str(e)}"


def send_file_and_query(query: str, file) -> tuple[bool, str]:
    """
    Send a file and query to the backend API.
    
    Args:
        query: User's health query
        file: Uploaded file object
        
    Returns:
        Tuple of (success, response_or_error)
    """
    try:
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        data = {"query": query}
        
        response = requests.post(
            f"{BACKEND_URL}/api/upload",
            data=data,
            files=files,
            timeout=120  # Longer timeout for file processing
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                return True, result.get("response", "No response content")
            else:
                return False, result.get("message", "Unknown error")
        else:
            return False, f"Server error (Status {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to the backend server. Please ensure it's running."
    except requests.exceptions.Timeout:
        return False, "Request timed out. File processing may take longer. Please try again."
    except Exception as e:
        return False, f"Error: {str(e)}"


# App title and description
st.title("🏥 HealthCare Assistant")
st.markdown("""
**Your AI-powered health companion.** Ask any health-related questions or upload your medical reports for personalized advice.

> ⚠️ **Important:** This is an AI assistant and **not** a substitute for professional medical advice, diagnosis, or treatment. 
> Always seek the advice of qualified health providers with any questions you may have regarding medical conditions.
""")

# Check backend health
backend_healthy = check_backend_health()
if not backend_healthy:
    st.warning(
        "⚠️ **Backend Connection Issue**: Cannot connect to the backend server at "
        f"`{BACKEND_URL}`. Please ensure the FastAPI backend is running. "
        "Run `python run.py` or `uvicorn app.main:app --reload` to start it."
    )

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

# Sidebar
with st.sidebar:
    st.header("💡 Tips & Information")
    
    st.markdown("""
    ### How to Use
    1. **Ask Questions**: Type your health-related questions in the chat
    2. **Upload Reports**: Attach PDF medical reports for context-aware advice
    3. **Get Insights**: Receive AI-powered health information
    
    ### Best Practices
    - Be specific with your questions
    - Upload relevant medical documents
    - Review responses critically
    - Consult professionals for serious concerns
    """)
    
    st.divider()
    
    st.markdown("""
    ### ⚠️ Disclaimer
    This AI assistant provides general health information only. It does NOT:
    - Diagnose medical conditions
    - Prescribe medications
    - Replace professional medical advice
    
    **For emergencies, call 911 or your local emergency number immediately.**
    """)
    
    st.divider()
    
    # Backend status indicator
    st.markdown("### 🔌 Backend Status")
    if backend_healthy:
        st.success("✅ Connected")
    else:
        st.error("❌ Disconnected")
    
    st.caption(f"Backend URL: `{BACKEND_URL}`")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# File uploader in main area (above chat input)
col1, col2 = st.columns([3, 1])
with col1:
    uploaded_file = st.file_uploader(
        "📄 Upload a medical report (PDF)", 
        type=["pdf"],
        help="Upload lab results, medical reports, or health records for more personalized advice"
    )

with col2:
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")
        if st.button("🗑️ Clear", key="clear_file"):
            uploaded_file = None
            st.session_state.uploaded_file = None
            st.rerun()

# Store uploaded file in session state
if uploaded_file:
    st.session_state.uploaded_file = uploaded_file

# Chat input
if prompt := st.chat_input("Ask me anything about health..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant message placeholder
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 Thinking...")
        
        # Determine which endpoint to use
        file_to_send = st.session_state.get("uploaded_file")
        
        if file_to_send:
            # Send file and query
            success, response = send_file_and_query(prompt, file_to_send)
        else:
            # Send chat-only query
            success, response = send_chat_message(prompt)
        
        # Update the placeholder with the response
        message_placeholder.empty()
        
        if success:
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response, unsafe_allow_html=True)
        else:
            error_message = f"❌ **Error**: {response}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})
            with st.chat_message("assistant"):
                st.error(error_message)
        
        # Clear uploaded file after processing (optional)
        # Uncomment the following lines if you want to clear the file after each query
        # if file_to_send:
        #     st.session_state.uploaded_file = None
        #     st.rerun()

# Footer
st.markdown("---")
st.caption(
    "Powered by Google Gemini AI • Built with FastAPI & Streamlit • "
    "Your health data is handled securely"
)
