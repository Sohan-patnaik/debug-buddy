from agents.retrieval_agent import Retrieve
from core.llm_client import LLM
from core.logger import get_logger
from langchain_core.prompts import PromptTemplate
from schemas.schema import BugAnalysis

logger = get_logger(__name__)

SYSTEM = """
Analyze the code and identify the root cause of the error.

Code:
{code}

Context:
{context}

Return a clear explanation of the root cause.
"""


class Bug:
    def __init__(self):
        self.model = LLM().get_llm()
        self.retriever = Retrieve()

    async def analyze(self):
        context_docs = await self.retriever.store()

        context = "\n\n".join(
            [doc.page_content for doc in context_docs]
        )


        prompt = PromptTemplate(
            template=SYSTEM,
            input_variables=["code", "context"]
        )

        formatted_prompt = prompt.format(
            code=self.retriever.code_context.code,
            context=context
        )


        result = self.model.invoke(formatted_prompt)

        return BugAnalysis(
            root_cause=str(result)
        )