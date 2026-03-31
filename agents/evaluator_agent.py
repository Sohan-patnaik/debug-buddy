from schemas.schema import Evaluation, FixGenerator
from langchain_core.prompts import PromptTemplate
from core.logger import get_logger
from core.llm_client import LLM
import json

logger = get_logger(__name__)

SYSTEM = """
You are a senior software engineer reviewing corrected code:

{code}

Evaluate using:

1. Static Validity (0-1)
2. Semantic Alignment (0-1)
3. Regression Risk (0-1, lower is better)

Then compute:
score = (validity + code_fix + (1 - regression_risk)) / 3

Return JSON:
{
  "validity": float,
  "code_fix": float,
  "regression_risk": float,
  "score": float,
  "feedback": "how to improve the fix"
}
"""


class Evaluator():

    def evaluation(self, code: FixGenerator):
        correctCode = code.correct_code

        prompt = PromptTemplate(
            template=SYSTEM,
            input_variables=["code"]
        )

        formatted_prompt = prompt.format(code=correctCode)

        model = LLM.get_llm()
        result = model.invoke(formatted_prompt)

        try:
            parsed = json.loads(result)
        except Exception:
            parsed = {
                "validity": str(result),
                "code_fix": "Could not parse structured output",
                "regression_risk": "N/A",
                "score":"N/A",
                "feedback":"N/A",
            }

        return Evaluation(
            validity=parsed["validity"],
            code_fix=parsed["code_fix"],
            regression_risk=parsed["regression_risk"],
            score=parsed["score"],
            feedback=parsed["feedback"]
        )
