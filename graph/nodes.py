from agents.retrieval_agent import Retrieve
from agents.bug_analyzer import Bug
from agents.fix_generator import Generate
from agents.evaluator_agent import Evaluator
from schemas.schema import CodeInput
from graph.state import AgentState
from agents.refinement_loop import RefinementAgent


async def retrieve(state: AgentState) -> AgentState:
    retriever = Retrieve()
    retriever.code_context = CodeInput(
        code=state["code"], error=state["error"])
    docs = await retriever.store()
    return {**state, "context_docs": docs}


async def analyze_bug(state: AgentState) -> AgentState:
    agent = Bug()
    result = await agent.analyze()
    return {**state, "bug_analysis": result}


async def fix_generate(state: AgentState) -> AgentState:
    generate = Generate()
    result = await generate.analyze()
    return {**state, "fix": result}


async def evaluate(state: AgentState) -> AgentState:
    evaluator = Evaluator()
    result = evaluator.evaluation()
    history = state["history"] + [{
        "iteration": state["iterations"]+1,
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
    refine = RefinementAgent()
    result = await refine.run()
    return {**state, "code": result}
