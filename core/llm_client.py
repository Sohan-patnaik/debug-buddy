from core.logger import get_logger
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
logger = get_logger(__name__)


class LLM():
    def __init__(self):
        provider = os.getenv("LLM_PROVIDER", "nvidia").lower()
        
        openai_key = os.getenv("OPENAI_API_KEY")
        google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        nvidia_key = os.getenv("NVIDIA_API_KEY")

        if provider == "openai" and openai_key:
            try:
                from langchain_openai import ChatOpenAI
                logger.info("Initializing ChatOpenAI model")
                self.client = ChatOpenAI(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    api_key=openai_key,
                    temperature=0.2
                )
                return
            except ImportError:
                logger.warning("LLM_PROVIDER is 'openai' but 'langchain-openai' package not installed. Falling back to NVIDIA.")

        elif provider == "gemini" and google_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                logger.info("Initializing ChatGoogleGenerativeAI model")
                self.client = ChatGoogleGenerativeAI(
                    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                    api_key=google_key,
                    temperature=0.2
                )
                return
            except ImportError:
                logger.warning("LLM_PROVIDER is 'gemini' but 'langchain-google-genai' package not installed. Falling back to NVIDIA.")

        logger.info("Initializing ChatNVIDIA model")
        self.client = ChatNVIDIA(
            model=os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-nano-30b-a3b"),
            api_key=nvidia_key,
            temperature=1,
            top_p=1,
            max_tokens=16384,
        )

    def get_llm(self):
        return self.client
