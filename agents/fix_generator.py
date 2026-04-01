from core.llm_client import LLM
from core.logger import get_logger
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from schemas.schema import FixGenerator, CodeInput, BugAnalysis
import json
import re

logger = get_logger(__name__)

SYSTEM = """You are a senior software engineer.

A bug has been identified in the code below. Fix it.

Error:
{error}

Root cause analysis:
{root_cause}

Code:
{code}

Retrieved context:
{context}

Return ONLY valid JSON with no markdown fences, no explanation outside JSON:
{{
  "correct_code": "full corrected code as a string",
  "explanation": "what was wrong and what you changed",
  "improvement_suggestions": "optional further improvements"
}}
"""


def _extract_json(text: str) -> dict:
    """Strip markdown fences and parse JSON robustly."""
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("```").strip()
    return json.loads(text)


class Generate:
    def __init__(self, state: CodeInput, context_docs: list[Document] = None, bug_analysis: BugAnalysis = None):
        self.model = LLM().get_llm()
        self.code_context = state
        self.context_docs = context_docs or []
        self.bug_analysis = bug_analysis

    async def analyze(self) -> FixGenerator:
        logger.info("Generating fix")

        context = "\n\n".join(doc.page_content for doc in self.context_docs)
        root_cause = self.bug_analysis.root_cause if self.bug_analysis else "Unknown"

        prompt = PromptTemplate(
            template=SYSTEM,
            input_variables=["error", "root_cause", "code", "context"]
        )

        formatted_prompt = prompt.format(
            error=self.code_context.error,
            root_cause=root_cause,
            code=self.code_context.code,
            context=context or "No external context available.",
        )

        result = self.model.invoke(formatted_prompt)
        raw = result.content if hasattr(result, "content") else str(result)

        try:
            parsed = _extract_json(raw)
        except Exception as e:
            logger.warning(f"JSON parse failed: {e} — using raw output")
            parsed = {
                "correct_code": raw,
                "explanation": "Could not parse structured output",
                "improvement_suggestions": "N/A",
            }

        logger.info("Fix generated successfully")
        return FixGenerator(
            correct_code=parsed["correct_code"],
            explanation=parsed["explanation"],
            improvement_suggestions=parsed["improvement_suggestions"],
        )