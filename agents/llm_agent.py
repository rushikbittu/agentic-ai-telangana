import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("[ERROR] Gemini API key not found. Please set GEMINI_API_KEY in .env")

def call_gemini_llm(prompt: str, model: str = DEFAULT_GEMINI_MODEL) -> str:
    """Calls Gemini Generative AI API."""
    if not GEMINI_API_KEY:
        return "Gemini API key not configured."
    try:
        model = genai.GenerativeModel(model)
        response = model.generate_content(prompt)
        return response.text if response and response.text else "No response from Gemini."
    except Exception as e:
        print(f"[LLM ERROR: Gemini] {e}")
        return "LLM unavailable, using fallback response."

def call_llm(prompt: str, config: dict) -> str:
    """
    Always calls Gemini (since OpenAI is removed).
    """
    llm_config = config.get("llm", {})
    model = llm_config.get("model", DEFAULT_GEMINI_MODEL)
    return call_gemini_llm(prompt, model)

def call_llm_for_cleaning_suggestions(sample_data, config: dict) -> str:
    """Ask LLM for cleaning suggestions given a sample of raw data."""
    prompt = (
        f"Suggest data cleaning steps for this data sample:\n"
        f"{json.dumps(sample_data, indent=2)}"
    )
    return call_llm(prompt, config)

def answer_question(user_question: str, transformed_path: str, config: dict) -> str:
    """Ask LLM a question about the transformed dataset."""
    try:
        with open(transformed_path, "r", encoding="utf-8") as f:
            data_snippet = "".join([next(f) for _ in range(20)])
    except Exception as e:
        print(f"[ERROR] Could not read transformed data: {e}")
        data_snippet = ""

    prompt = f"Data snippet:\n{data_snippet}\n\nQuestion: {user_question}"
    return call_llm(prompt, config)
