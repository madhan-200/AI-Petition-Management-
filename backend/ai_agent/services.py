import os
import google.generativeai as genai

# Ensure GOOGLE_API_KEY is set in environment
# os.environ["GOOGLE_API_KEY"] = "..."

def get_model():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Warning: GOOGLE_API_KEY not found. AI features will be disabled.")
        return None
    
    # Configure REST transport to avoid gRPC blocking
    genai.configure(api_key=api_key, transport='rest')
    return genai.GenerativeModel('gemini-2.0-flash')

def classify_department(title, description):
    model = get_model()
    if not model:
        return "General"
    
    prompt = f"""
    You are an AI assistant for a government grievance system.
    Classify the following petition into one of these departments:
    [Roads & Transport, Electricity, Water Supply, Sanitation, Police, Health, Education, General]
    
    Petition Title: {title}
    Petition Description: {description}
    
    Return ONLY the department name.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"AI Classification failed: {e}")
        return "General"

def predict_urgency(title, description):
    model = get_model()
    if not model:
        return "LOW"
    
    prompt = f"""
    You are an AI assistant. Analyze the urgency of this petition.
    Urgency Levels: [LOW, MEDIUM, HIGH, CRITICAL]
    
    Criteria:
    - CRITICAL: Life-threatening, severe safety hazard, massive public disruption.
    - HIGH: Major inconvenience, potential safety risk, urgent health issue.
    - MEDIUM: Standard grievance, non-urgent repair needed.
    - LOW: Suggestions, minor complaints, non-time-sensitive.
    
    Petition Title: {title}
    Petition Description: {description}
    
    Return ONLY the urgency level.
    """
    
    try:
        response = model.generate_content(prompt)
        urgency = response.text.strip().upper()
        if urgency not in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
            return 'LOW'
        return urgency
    except Exception as e:
        print(f"AI Urgency Prediction failed: {e}")
        return "LOW"
