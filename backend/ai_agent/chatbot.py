import google.generativeai as genai
import os
from typing import List, Dict

def get_chatbot_model():
    """Initialize Gemini model for chatbot conversations."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None
    
    genai.configure(api_key=api_key, transport='rest')
    
    # Use Gemini with chat-optimized configuration
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 1024,
    }
    
    model = genai.GenerativeModel(
        'gemini-2.0-flash',
        generation_config=generation_config
    )
    
    return model

def get_chatbot_response(user_message: str, conversation_history: List[Dict] = None) -> str:
    """
    Get chatbot response from Gemini.
    
    Args:
        user_message: The user's message
        conversation_history: List of previous messages [{"role": "user"|"assistant", "content": "..."}]
    
    Returns:
        Chatbot response text
    """
    model = get_chatbot_model()
    
    if not model:
        return "I'm sorry, the chatbot service is currently unavailable. Please try again later."
    
    try:
        # Build conversation context
        system_prompt = """You are a helpful AI assistant for a government petition and grievance management system. 
Your role is to:
1. Help citizens understand how to submit petitions
2. Explain the petition process and status meanings
3. Answer questions about departments and urgency levels
4. Provide general guidance on using the system

Be concise, professional, and helpful. If asked about specific petition details, remind users to check their dashboard."""

        # Combine system prompt with conversation history
        full_prompt = f"{system_prompt}\n\n"
        
        if conversation_history:
            for msg in conversation_history[-5:]:  # Keep last 5 messages for context
                role = "User" if msg["role"] == "user" else "Assistant"
                full_prompt += f"{role}: {msg['content']}\n"
        
        full_prompt += f"User: {user_message}\nAssistant:"
        
        # Generate response
        response = model.generate_content(full_prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
    
    except Exception as e:
        print(f"Chatbot error: {e}")
        return "I encountered an error processing your message. Please try again or contact support if the issue persists."

def get_petition_help(topic: str = "general") -> str:
    """Get help text for specific petition-related topics."""
    
    help_topics = {
        "submit": """To submit a petition:
1. Click 'Submit Petition' in the navigation
2. Fill in the title and description clearly
3. Attach any supporting documents (photos, PDFs)
4. Click Submit - our AI will automatically classify it to the right department
5. You'll receive a petition ID to track your submission""",
        
        "status": """Petition Status Meanings:
- SUBMITTED: Your petition has been received
- UNDER_REVIEW: Being reviewed by the department
- ASSIGNED: Assigned to an officer for action
- IN_PROGRESS: Officer is working on resolution
- RESOLVED: Issue has been resolved
- REJECTED: Petition was rejected (you'll receive a reason)
- CLOSED: Petition has been closed""",
        
        "urgency": """Urgency Levels (AI-determined):
- CRITICAL: Life-threatening or severe safety hazard
- HIGH: Major inconvenience or potential safety risk
- MEDIUM: Standard grievance requiring attention
- LOW: Suggestions or minor complaints

Our AI analyzes your petition to determine urgency automatically.""",
        
        "departments": """Available Departments:
- Roads & Transport
- Electricity
- Water Supply
- Sanitation
- Police
- Health
- Education
- General

Our AI automatically routes your petition to the correct department based on your description.""",
        
        "general": """Welcome to the AI Petition System!

I can help you with:
- How to submit a petition
- Understanding petition status
- Explaining urgency levels
- Information about departments
- General system guidance

What would you like to know?"""
    }
    
    return help_topics.get(topic, help_topics["general"])
