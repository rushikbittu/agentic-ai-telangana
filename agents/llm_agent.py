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


class LLMAgent:
    """Unified interface for interacting with Gemini LLM."""

    def __init__(self, config: dict = None, model_name: str = None):
        """
        Initialize LLMAgent.

        Supports:
        - LLMAgent(config)  -> preferred
        - LLMAgent(model_name="gemini-1.5-flash") -> backward compatibility
        """
        if config:
            self.config = config
            self.model_name = config.get("llm", {}).get("model", DEFAULT_GEMINI_MODEL)
        else:
            self.config = {}
            self.model_name = model_name or DEFAULT_GEMINI_MODEL

    def call_gemini_llm(self, prompt: str) -> str:
        """Calls Gemini Generative AI API."""
        if not GEMINI_API_KEY:
            return "Gemini API key not configured."
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            return response.text if response and response.text else "No response from Gemini."
        except Exception as e:
            print(f"[LLM ERROR: Gemini] {e}")
            return "LLM unavailable, using fallback response."

    def ask(self, prompt: str) -> str:
        """Ask Gemini a general question."""
        return self.call_gemini_llm(prompt)

    def cleaning_suggestions(self, sample_data) -> str:
        """Ask Gemini for cleaning suggestions given a sample of raw data."""
        prompt = (
            f"Suggest data cleaning steps for this data sample:\n"
            f"{json.dumps(sample_data, indent=2)}"
        )
        return self.ask(prompt)

    def answer_question(self, user_question: str, transformed_path: str) -> str:
        """Ask Gemini a question about the transformed dataset."""
        try:
            with open(transformed_path, "r", encoding="utf-8") as f:
                data_snippet = "".join([next(f) for _ in range(20)])
        except Exception as e:
            print(f"[ERROR] Could not read transformed data: {e}")
            data_snippet = ""

        prompt = f"Data snippet:\n{data_snippet}\n\nQuestion: {user_question}"
        return self.ask(prompt)


# Keep backward-compatible function for cleaning.py
def call_llm_for_cleaning_suggestions(sample_data, config: dict) -> str:
    """Compatibility wrapper for cleaning agent."""
    agent = LLMAgent(config)
    return agent.cleaning_suggestions(sample_data)
