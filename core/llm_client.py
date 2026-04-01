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
        api_key = os.getenv("NVIDIA_API_KEY")
        self.client = ChatNVIDIA(
            model="nvidia/nemotron-3-nano-30b-a3b",
            api_key=api_key,
            temperature=1,
            top_p=1,
            max_tokens=16384,
            model_kwargs={"enable_thinking": True},
        )

    def get_llm(self):
        return self.client
