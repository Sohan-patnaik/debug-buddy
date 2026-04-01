from schemas.schema import Evaluation, FixGenerator
from langchain_core.prompts import PromptTemplate
from core.logger import get_logger
from core.llm_client import LLM
import json
import re

logger = get_logger(__name__)

SYSTEM = """You are a senior code reviewer.

Evaluate the corrected code below against the original error.

Original error:
{error}

Corrected code:
{code}

Score on three axes (each 0.0–1.0):
1. validity      — is the code syntactically and logically correct?
2. code_fix      — does it actually fix the reported error?
3. regression_risk — how likely is it to break something else? (lower = better)

Compute: score = (validity + code_fix + (1 - regression_risk)) / 3

Return ONLY valid JSON, no markdown fences:
{{
  "validity": float,
  "code_fix": float,
  "regression_risk": float,
  "score": float,
  "feedback": "concrete suggestion to improve the fix further"
}}
"""


def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("```").strip()
    return json.loads(text)


class Evaluator:

    async def evaluation(self, code: FixGenerator, error: str = "") -> Evaluation:
        logger.info("Evaluating fix")

        prompt = PromptTemplate(
            template=SYSTEM,
            input_variables=["error", "code"]
        )

        formatted_prompt = prompt.format(
            error=error,
            code=code.correct_code,
        )

        model = LLM().get_llm()
        result = model.invoke(formatted_prompt)
        raw = result.content if hasattr(result, "content") else str(result)

        try:
            parsed = _extract_json(raw)
        except Exception as e:
            logger.warning(f"Evaluator JSON parse failed: {e} — assigning low score")
            parsed = {
                "validity": 0.0,
                "code_fix": 0.0,
                "regression_risk": 1.0,
                "score": 0.0,
                "feedback": f"Could not parse evaluator output: {raw[:200]}",
            }

        logger.info(f"Evaluation score: {parsed['score']:.2f}")
        return Evaluation(
            validity=parsed["validity"],
            code_fix=parsed["code_fix"],
            regression_risk=parsed["regression_risk"],
            score=parsed["score"],
            feedback=parsed["feedback"],
        )