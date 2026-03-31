from typing import TypedDict, Optional, List
from schemas.schema import BugAnalysis, FixGenerator, Evaluation

class AgentState(TypedDict):
    code: str
    error: str
    context_docs: list
    bug_analysis: Optional[BugAnalysis]
    fix: Optional[FixGenerator]
    evaluation: Optional[Evaluation]
    iterations: int
    history: List[dict]
    final_code: Optional[str]