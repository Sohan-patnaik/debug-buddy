from core.llm_client import LLM
from core.logger import get_logger
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from schemas.schema import BugAnalysis, CodeInput
import json
import re

logger = get_logger(__name__)

SYSTEM = """You are an expert software debugger.

Analyze the code below and identify the root cause of the reported error.
Use the retrieved context only if it is relevant — ignore it otherwise.

Error:
{error}

Code:
{code}

Retrieved context:
{context}

Return ONLY valid JSON, no markdown fences, no extra text:
{{
  "error_category": "runtime" or "logical" or "syntax",
  "root_cause": "1-2 sentence precise explanation of why it fails",
  "responsible_lines": "line numbers or function names responsible",
  "summary": "one-line tldr"
}}
"""


def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    return json.loads(text)


class Bug:
    def __init__(self, state: CodeInput, context_docs: list[Document] = None):
        self.model = LLM().get_llm()
        self.code_context = state
        self.context_docs = context_docs or []

    async def analyze(self) -> BugAnalysis:
        logger.info("Running bug analysis")

        context = "\n\n".join(doc.page_content for doc in self.context_docs)

        prompt = PromptTemplate(
            template=SYSTEM,
            input_variables=["error", "code", "context"]
        )

        formatted_prompt = prompt.format(
            error=self.code_context.error,
            code=self.code_context.code,
            context=context or "No external context available.",
        )

        result = self.model.invoke(formatted_prompt)
        raw = result.content if hasattr(result, "content") else str(result)

        try:
            parsed = _extract_json(raw)
        except Exception as e:
            logger.warning(f"BugAnalysis JSON parse failed: {e} — using fallback")
            parsed = {
                "error_category": "runtime",
                "root_cause": raw,
                "responsible_lines": "unknown",
                "summary": "Could not parse structured output",
            }

        logger.info(f"Bug analysis complete — category: {parsed['error_category']}")

        return BugAnalysis(
            error_category=parsed["error_category"],
            root_cause=parsed["root_cause"],
            responsible_lines=parsed.get("responsible_lines"),
            summary=parsed.get("summary"),
        )