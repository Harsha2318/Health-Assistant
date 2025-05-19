import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from the root .env file
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file in the project root.")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-2.0-flash')

async def get_health_advice(query: str, file_text: str = None) -> str:
    """
    Get health advice using Gemini model.
    
    Args:
        query (str): User's health query
        file_text (str, optional): Extracted text from uploaded PDF. Defaults to None.
    
    Returns:
        str: Generated health advice
    """
    try:
        if not query or not query.strip():
            return "Please provide a valid health-related question."
            
        print(f"Generating response for query: {query[:100]}...")
        
        # Create the prompt
        prompt = f"""You are a helpful and empathetic healthcare assistant. 
        Provide clear, accurate, and easy-to-understand health information.
        If the query is about a medical emergency, advise seeking immediate professional help.
        
        User's query: {query}
        """
        
        # Add file content if available
        if file_text and file_text.strip():
            prompt += f"\n\nAdditional information from user's health records:\n{file_text}"
        
        print(f"Sending prompt to Gemini...")
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            return "I'm sorry, I couldn't generate a response. Please try again with a different query."
            
        print(f"Successfully received response from Gemini")
        return response.text
        
    except Exception as e:
        error_msg = f"Error generating health advice: {str(e)}"
        print(error_msg)
        import traceback
        print(traceback.format_exc())
        return error_msg
