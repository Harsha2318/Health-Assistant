import streamlit as st

# Set page config - MUST be the first Streamlit command
st.set_page_config(
    page_title="HealthCare Assistant",
    page_icon="🏥",
    layout="wide"
)

import base64
import os
import sys
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the root .env file
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import tools
from app.agents.gemini_tool import get_health_advice
from app.agents.dropbox_tool import upload_and_read_pdf

# Custom CSS for better chat interface
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Main background */
    .main {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* Text color for better contrast */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* Chat container */
    .stChatFloatingInputContainer {
        background-color: #1a1a1a;
    }
    
    /* Input field */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        background-color: #333333;
        color: #ffffff;
    }
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
    .stTextArea>div>div>textarea {
        min-height: 150px;
    }
    .file-uploader {
        border: 2px dashed #4CAF50;
        border-radius: 5px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# App title and description
st.title("🏥 HealthCare Assistant")
st.markdown("""
Ask any health-related questions or upload your medical reports for personalized advice.
**Note:** This is an AI assistant and not a substitute for professional medical advice.
""")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history with proper formatting
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Clean and format the message content
        content = message["content"]
        # Replace common markdown patterns with HTML equivalents
        content = content.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
        content = content.replace('*', '<em>', 1).replace('*', '</em>', 1)
        content = content.replace('_', '\_')  # Escape underscores
        
        # Convert newlines to <br> for HTML display
        content = content.replace('\n', '<br>')
        
        # Display with HTML for better formatting
        st.markdown(f"""
        <div style="
            background-color: #1e1e1e;
            padding: 1.2rem;
            border-radius: 0.8rem;
            margin: 0.8rem 0;
            line-height: 1.8;
            color: #f0f0f0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            border-left: 4px solid #4CAF50;
        ">
            <div style="
                max-width: 100%;
                overflow-wrap: break-word;
                word-wrap: break-word;
                white-space: pre-wrap;
            ">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader(
    "📄 Upload a medical report (PDF only)", 
    type=["pdf"],
    accept_multiple_files=False,
    key="file_uploader"
)

# Chat input
if prompt := st.chat_input("Ask me anything about health..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Show loading message
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # Prepare the request to the FastAPI backend
            files = {}
            if uploaded_file is not None:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            
            data = {"query": prompt}
            
            # Make the API call
            try:
                with st.spinner('Thinking...'):
                    response = requests.post(
                        "http://localhost:8000/api/health-advice",
                        data=data,
                        files=files if files else None,
                        timeout=60  # 60 seconds timeout
                    )
                    
                    print(f"API Response Status: {response.status_code}")
                    print(f"API Response: {response.text}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("status") == "success":
                            full_response = result.get("response", "No response content")
                            # Clear the loading message
                            message_placeholder.empty()
                            # Add the response to chat history
                            st.session_state.messages.append({"role": "assistant", "content": full_response})
                            # Rerun to update the UI
                            st.rerun()
                        else:
                            error_msg = result.get("message", "An unknown error occurred")
                            st.error(f"❌ {error_msg}")
                            st.session_state.messages.append({"role": "assistant", "content": f"Error: {error_msg}"})
                    else:
                        error_msg = f"Failed to get response (Status code: {response.status_code})"
                        if response.text:
                            error_msg += f"\n{response.text}"
                        st.error(f"❌ {error_msg}")
                        st.session_state.messages.append({"role": "assistant", "content": f"Error: {error_msg}"})
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Failed to connect to the server: {str(e)}"
                st.error(f"❌ {error_msg}")
                st.session_state.messages.append({"role": "assistant", "content": f"Connection error: {str(e)}"})
                print(f"Request Exception: {str(e)}")
                st.rerun()
                
        except Exception as e:
            message_placeholder.markdown(f"❌ Error: {str(e)}")

# Add some helpful tips
st.sidebar.markdown("## 💡 Tips")
st.sidebar.markdown("""
- Be specific with your health questions
- Upload relevant medical reports for more accurate advice
- For emergencies, contact healthcare professionals immediately
- Keep your personal information private
""")

# Add a disclaimer
st.sidebar.markdown("## ⚠️ Disclaimer")
st.sidebar.markdown("""
This is an AI assistant and not a substitute for professional medical advice. 
Always consult with a qualified healthcare provider for any health concerns.
""")
