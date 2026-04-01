from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.nodes import retrieve, analyze_bug, generate_fix, evaluate, refine


def build_graph(threshold: float = 0.8, max_iters: int = 3):
    def should_refine(state: AgentState) -> str:
        if state["evaluation"].score >= threshold:
            return "accept"
        if state["iterations"] >= max_iters:
            return "accept"
        return "refine"
    g = StateGraph(AgentState)
    g.add_node("retrieve", retrieve)
    g.add_node("analyze_bug", analyze_bug)
    g.add_node("generate_fix", generate_fix)
    g.add_node("evaluate", evaluate)
    g.add_node("refine", refine)

    g.set_entry_point("retrieve")
    g.add_edge("retrieve", "analyze_bug")
    g.add_edge("analyze_bug", "generate_fix")
    g.add_edge("generate_fix", "evaluate")

    g.add_conditional_edges(
        "evaluate",
        should_refine,
        {
            "refine": "refine",
            "accept": END
        }
    )
    g.add_edge("refine", "generate_fix")
    return g.compile()


graph = build_graph()
