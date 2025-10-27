import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Groq API Settings
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile")

    # Processing Settings
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1500))
    OVERLAP_SIZE = int(os.getenv("OVERLAP_SIZE", 150))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 3000))  # Increased
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.8))  # Increased for diversity
    CONTEXT_LINES = int(os.getenv("CONTEXT_LINES", 5))

    # Application Settings
    ENABLE_CHUNKING = os.getenv("ENABLE_CHUNKING", "true").lower() == "true"
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

    @classmethod
    def validate_config(cls):
        if not cls.GROQ_API_KEY:
            print("❌ WARNING: GROQ_API_KEY not found in .env file.")
            print("💡 Please add your Groq API key to the .env file:")
            print("   GROQ_API_KEY=your_actual_groq_api_key_here")
            print("   You can get a free API key from: https://console.groq.com/")

        # Current available Groq models
        available_models = [
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ]

        if cls.MODEL_NAME not in available_models:
            print(
                f"⚠️  Warning: Model {cls.MODEL_NAME} might not be available. Using default: {cls.DEFAULT_MODEL}"
            )
            cls.MODEL_NAME = cls.DEFAULT_MODEL

        print(
            f"✅ Configuration loaded: {cls.MODEL_NAME} (Tokens: {cls.MAX_TOKENS}, Temp: {cls.TEMPERATURE})"
        )
