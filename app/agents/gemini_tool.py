"""
Gemini AI Integration for Health-Assistant
Provides healthcare advice using Google's Gemini 1.5 Flash model.
"""
import os
import logging
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Load environment variables from the root .env file
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

# Configure logging
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError(
        "GEMINI_API_KEY not found in environment variables. "
        "Please check your .env file in the project root."
    )

genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model with safety settings
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

# Use gemini-1.5-flash as specified in requirements
MODEL_NAME = "gemini-1.5-flash"

try:
    model = genai.GenerativeModel(MODEL_NAME)
    logger.info(f"Successfully initialized Gemini model: {MODEL_NAME}")
except Exception as e:
    logger.error(f"Failed to initialize Gemini model: {str(e)}")
    raise


# Healthcare system prompt template
HEALTHCARE_SYSTEM_PROMPT = """You are a helpful, empathetic, and knowledgeable healthcare assistant AI. 
Your role is to provide accurate, evidence-based, and easy-to-understand health information while being compassionate and supportive.

CRITICAL GUIDELINES YOU MUST FOLLOW:

1. PATIENT SAFETY FIRST:
   - If symptoms suggest a medical emergency (chest pain, severe bleeding, difficulty breathing, suicidal thoughts, etc.), 
     IMMEDIATELY advise seeking emergency medical help (call 911 or local emergency number).
   - Never delay someone from seeking professional care when needed.

2. SCOPE OF ASSISTANCE:
   - Provide general health information and education based on established medical knowledge.
   - Explain medical terms, conditions, treatments, and procedures in accessible language.
   - Discuss lifestyle modifications, preventive care, and wellness strategies.
   - Help users understand their symptoms and when to seek professional care.

3. LIMITATIONS - ALWAYS CLARIFY:
   - You CANNOT diagnose conditions definitively.
   - You CANNOT prescribe medications or adjust dosages.
   - You CANNOT replace personalized medical advice from a qualified healthcare provider.
   - Always recommend consulting with healthcare professionals for:
     * Persistent or worsening symptoms
     * New or unexplained symptoms
     * Questions about medications or treatments
     * Personalized medical advice

4. COMMUNICATION STYLE:
   - Be warm, empathetic, and non-judgmental.
   - Use clear, simple language avoiding unnecessary medical jargon.
   - When technical terms are necessary, explain them clearly.
   - Acknowledge the user's concerns and validate their feelings.
   - Provide balanced information without causing unnecessary alarm.

5. EVIDENCE-BASED INFORMATION:
   - Base responses on established medical guidelines and scientific evidence.
   - If uncertain about something, acknowledge the limitation.
   - Distinguish between well-established facts and emerging research.
   - Mention when there are multiple valid approaches to a health concern.

6. PRIVACY AND SENSITIVITY:
   - Handle all health information with utmost sensitivity.
   - Remind users not to share highly sensitive personal information.
   - Respect cultural differences in health beliefs and practices.

7. WHEN ANALYZING MEDICAL DOCUMENTS:
   - Reference specific findings from the provided documents.
   - Explain what test results might mean in general terms.
   - Clarify that interpretation should be confirmed by their healthcare provider.
   - Connect document findings to the user's specific questions.

RESPONSE FORMAT:
- Start with empathy and acknowledgment of their concern.
- Provide clear, organized information using paragraphs or bullet points.
- Include relevant context and explanations.
- End with actionable next steps or recommendations.
- Always include an appropriate disclaimer when giving health information.

Remember: Your goal is to empower users with knowledge while ensuring they seek appropriate professional care when needed."""


async def get_health_advice(query: str, file_text: Optional[str] = None) -> str:
    """
    Get health advice using Gemini model.
    
    Args:
        query: User's health query
        file_text: Optional text extracted from uploaded PDF
        
    Returns:
        Generated health advice as a string
    """
    try:
        # Validate input
        if not query or not query.strip():
            return "Please provide a valid health-related question."
        
        query = query.strip()
        logger.info(f"Processing health query (length: {len(query)} chars)")
        
        # Build the complete prompt
        if file_text and file_text.strip():
            # Truncate very long documents to avoid token limits
            max_doc_length = 15000
            if len(file_text) > max_doc_length:
                file_text = file_text[:max_doc_length] + "\n\n[Document truncated due to length...]"
            
            prompt = f"""{HEALTHCARE_SYSTEM_PROMPT}

---
USER'S MEDICAL DOCUMENT CONTENT:
{file_text}

---
USER'S QUESTION:
{query}

---
Please analyze the medical document content above (if relevant to the question) and provide a thoughtful, 
helpful response to the user's question. Reference specific details from their documents where applicable.
"""
        else:
            prompt = f"""{HEALTHCARE_SYSTEM_PROMPT}

---
USER'S QUESTION:
{query}

---
Please provide a helpful and informative response based on your medical knowledge.
"""
        
        logger.info("Sending request to Gemini API...")
        
        # Generate response with safety settings
        response = model.generate_content(
            prompt,
            safety_settings=SAFETY_SETTINGS
        )
        
        # Check if response is valid
        if not response:
            logger.warning("Empty response from Gemini API")
            return "I'm sorry, I couldn't generate a response. Please try again with a different query."
        
        # Check for blocked content
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            block_reason = response.prompt_feedback.block_reason.name
            logger.warning(f"Request was blocked: {block_reason}")
            return "I'm unable to respond to this query as it may involve sensitive content. Please rephrase your question or consult a healthcare professional directly."
        
        response_text = response.text
        
        if not response_text or not response_text.strip():
            logger.warning("Empty response text from Gemini API")
            return "I'm sorry, I couldn't generate a response. Please try again."
        
        logger.info(f"Successfully received response ({len(response_text)} chars)")
        return response_text.strip()
        
    except genai.types.BlockedPromptException as e:
        logger.warning(f"Prompt was blocked: {str(e)}")
        return "I'm unable to process this query due to safety guidelines. Please rephrase your question or consult a healthcare professional."
        
    except genai.types.StopCandidateException as e:
        logger.warning(f"Response was stopped: {str(e)}")
        return "The response was interrupted. Please try rephrasing your question."
        
    except Exception as e:
        error_msg = f"Error generating health advice: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return f"I apologize, but I encountered a technical issue while processing your request. Please try again later. (Error: {str(e)})"
