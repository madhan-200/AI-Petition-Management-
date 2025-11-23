import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")
print(f"API Key found: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("No API Key!")
    exit(1)

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key, temperature=0)

try:
    print("Invoking Gemini...")
    result = llm.invoke("Hello, are you working?")
    print(f"Result: {result.content}")
except Exception as e:
    print(f"Error: {e}")
