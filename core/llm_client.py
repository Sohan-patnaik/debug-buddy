from core.logger import get_logger
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
logger = get_logger(__name__)


class LLM():
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
        )

    def get_llm(self):
        return self.model
