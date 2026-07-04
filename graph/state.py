from typing import TypedDict, Optional, List
from schemas.schema import BugAnalysis, FixGenerator, Evaluation

class AgentState(TypedDict):
    filepath: str
    code: str
    error: str
    context_docs: list
    bug_analysis: Optional[BugAnalysis]
    fix: Optional[FixGenerator]
    evaluation: Optional[Evaluation]
    iterations: int
    history: List[dict]
    final_code: Optional[str]