from schemas.schema import FixGenerator
from core.llm_client import LLM
from agents.retrieval_agent import Retrieve
from langchain_core.prompts import PromptTemplate
import json


SYSTEM = """
You are a senior developer.

Given the following code and context, fix the issue.

Code:
{code}

Context:
{context}

Return your response strictly in JSON format:

{{
  "correct_code": "...",
  "explanation": "...",
  "improvement_suggestions": "..."
}}
"""


class Generate:
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

        try:
            parsed = json.loads(result)
        except Exception:
            parsed = {
                "correct_code": str(result),
                "explanation": "Could not parse structured output",
                "improvement_suggestions": "N/A"
            }

        return FixGenerator(
            correct_code=parsed["correct_code"],
            explanation=parsed["explanation"],
            improvement_suggestions=parsed["improvement_suggestions"]
        )