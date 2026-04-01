from agents.bug_analyzer import Bug
from agents.fix_generator import Generate
from agents.evaluator_agent import Evaluator
from agents.retrieval_agent import Retrieve
from schemas.schema import CodeInput
from graph.state import AgentState
from core.logger import get_logger

logger = get_logger(__name__)


async def retrieve(state: AgentState) -> AgentState:
    logger.info("Node: retrieve")
    code_input = CodeInput(code=state["code"], error=state["error"])
    retriever = Retrieve(code_input)
    docs = await retriever.store()
    return {**state, "context_docs": docs}


async def analyze_bug(state: AgentState) -> AgentState:
    logger.info("Node: analyze_bug")
    code_input = CodeInput(code=state["code"], error=state["error"])
    agent = Bug(state=code_input, context_docs=state["context_docs"])
    result = await agent.analyze()
    return {**state, "bug_analysis": result}


async def generate_fix(state: AgentState) -> AgentState:
    logger.info("Node: generate_fix")
    code_input = CodeInput(code=state["code"], error=state["error"])
    agent = Generate(
        state=code_input,
        context_docs=state["context_docs"],
        bug_analysis=state.get("bug_analysis"),
    )
    result = await agent.analyze()
    return {**state, "fix": result}


async def evaluate(state: AgentState) -> AgentState:
    logger.info("Node: evaluate")
    evaluator = Evaluator()
    result = await evaluator.evaluation(
        code=state["fix"],
        error=state["error"],
    )
    history = state["history"] + [{
        "iteration": state["iterations"] + 1,
        "score": result.score,
        "feedback": result.feedback,
    }]
    return {
        **state,
        "evaluation": result,
        "iterations": state["iterations"] + 1,
        "history": history,
    }


async def refine(state: AgentState) -> AgentState:
    logger.info(f"Node: refine (iteration {state['iterations']})")
    feedback = state["evaluation"].feedback

    refined_code = f"# FEEDBACK FROM EVALUATOR:\n# {feedback}\n\n{state['fix'].correct_code}"
    return {**state, "code": refined_code}