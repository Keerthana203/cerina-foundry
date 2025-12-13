from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from .safety import evaluate_safety



class GraphState(TypedDict):
    request_id: int
    version: int
    draft_text: str
    iteration: int
    safety_score: float
    empathy_score: float
    notes: List[Dict[str, Any]]


def drafter_agent(state: GraphState) -> GraphState:
    iteration = state.get("iteration", 0) + 1

    notes = list(state.get("notes", []))
    notes.append({
        "agent": "drafter",
        "message": f"Draft revision iteration {iteration}"
    })

    return {
        **state,
        "draft_text": state.get("draft_text", "") + "\n\n[DRAFT UPDATE]",
        "iteration": iteration,
        "notes": notes,
    }



def safety_agent(state: GraphState) -> GraphState:
    score = evaluate_safety(state["draft_text"])

    notes = list(state.get("notes", []))
    notes.append({
        "agent": "safety",
        "message": f"Safety score evaluated at {score}"
    })

    return {
        **state,
        "safety_score": score,
        "notes": notes,
    }


def critic_agent(state: GraphState) -> GraphState:
    notes = list(state.get("notes", []))
    notes.append({
        "agent": "critic",
        "message": "Clinical tone and empathy acceptable"
    })

    return {
        **state,
        "empathy_score": 0.9,
        "notes": notes,
    }


SAFETY_THRESHOLD = 0.8
MAX_ITERATIONS = 5


def supervisor_should_continue(state: GraphState) -> str:
    # Force at least one revision cycle
    if state["iteration"] < 1:
        return "revise"

    if state["safety_score"] < SAFETY_THRESHOLD:
        return "revise"

    if state["iteration"] >= MAX_ITERATIONS:
        return "halt"

    return "finalize"



def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("drafter", drafter_agent)
    graph.add_node("safety", safety_agent)
    graph.add_node("critic", critic_agent)

    graph.set_entry_point("drafter")
    graph.add_edge("drafter", "safety")
    graph.add_edge("safety", "critic")

    graph.add_conditional_edges(
        "critic",
        supervisor_should_continue,
        {
            "revise": "drafter",
            "halt": END,
            "finalize": END,
        },
    )

    return graph.compile()


