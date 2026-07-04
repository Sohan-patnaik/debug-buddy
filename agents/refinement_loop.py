from core.logger import get_logger
from core.llm_client import LLM
import json

logger=get_logger(__name__)

class RefinementAgent:

    def __init__(self, fixer, evaluator, threshold=0.8, max_iters=3):
        self.fixer = fixer
        self.evaluator = evaluator
        self.threshold = threshold
        self.max_iters = max_iters

    async def run(self, buggy_code: str):
        current_code = buggy_code
        history = []

        for i in range(self.max_iters):
            logger.info(f"Iteration {i+1}")

            fix_result = await self.fixer.analyze(current_code)

            eval_result = await self.evaluator.evaluation(fix_result)

            history.append({
                "iteration": i + 1,
                "score": eval_result.score,
                "feedback": eval_result.feedback
            })

            logger.info(f"Score: {eval_result.score}")

            if eval_result.score >= self.threshold:
                logger.info("Accepted fix")
                return {
                    "final_code": fix_result.correct_code,
                    "score": eval_result.score,
                    "iterations": history
                }

            # Step 4: Improve using feedback
            current_code = self._refine_with_feedback(
                fix_result.correct_code,
                eval_result.feedback
            )

        # fallback return
        return {
            "final_code": current_code,
            "score": eval_result.score,
            "iterations": history
        }

    def _refine_with_feedback(self, code: str, feedback: str):
        prompt = f"""You are a senior developer. Improve the following code based on feedback.
Return the corrected code directly inside JSON with key 'correct_code'. No markdown formatting outside JSON.

Code:
{code}

Feedback:
{feedback}
"""
        model = LLM().get_llm()
        result = model.invoke(prompt)
        content = result.content if hasattr(result, "content") else str(result)
        
        import re
        content_clean = re.sub(r"```(?:json)?", "", content).strip().rstrip("`").strip()
        
        try:
            parsed = json.loads(content_clean)
            return parsed.get("correct_code", code)
        except Exception:
            # Fallback to direct content if not JSON
            return content_clean or code