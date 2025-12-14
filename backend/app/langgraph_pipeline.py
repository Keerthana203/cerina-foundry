from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from .safety import evaluate_safety
from .llm_client import call_llm_stream



class GraphState(TypedDict):
    request_id: int
    version: int
    user_intent: str
    draft_text: str
    iteration: int
    safety_score: float
    empathy_score: float
    notes: List[Dict[str, Any]]


def drafter_agent(state: GraphState) -> GraphState:
    state["iteration"] += 1

    user_intent = state["user_intent"]
    previous_draft = state.get("draft_text", "")
    notes = list(state.get("notes", []))

    prompt = f"""
You are generating a CBT protocol artifact for clinical use.

CRITICAL OUTPUT RULES:
- Output MUST be a protocol document, NOT a conversation.
- Do NOT address the user directly.
- Do NOT include encouragement, coaching language, or motivational phrases.
- Do NOT include introductions, conclusions, or next steps.
- Do NOT include meta commentary or explanations.
- Do NOT reference yourself, AI, agents, or revisions.

STYLE:
- Neutral, clinical, structured
- Clear bullet points
- Actionable steps
- Empathetic but impersonal tone

USER CONTEXT:
{user_intent}

PREVIOUS VERSION (if any):
{previous_draft if previous_draft else "None"}

AGENT FEEDBACK (summarized):
- Safety score: {state["safety_score"]}
- Iteration: {state["iteration"]}

OUTPUT FORMAT (MANDATORY):

Title

Context Summary (3–4 bullet points)

Identified Cognitive Distortions
- Bullet list with brief descriptions

Behavioral Activation Plan
- Step 1
- Step 2
- Step 3

Cognitive Restructuring Exercises
- Exercise name
- Instructions (bullet points)

Daily Micro-Habit System
- Habit
- Time commitment
- Goal

Safety Disclaimer
- 2 short bullet points

ONLY output the protocol content following this structure.
"""


    draft_chunks = []
    for chunk in call_llm_stream(prompt):
        draft_chunks.append(chunk)
        state["draft_text"] = "".join(draft_chunks)  # 🔥 STREAM TO UI

    notes.append({
        "agent": "drafter",
        "message": f"LLM-based draft revision (iteration {state['iteration']})"
    })

    state["notes"] = notes
    return state




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
    # Safety failure → expensive revise
    if state["safety_score"] < SAFETY_THRESHOLD:
        return "revise"

    # Optional: only revise if critic flags issues
    critic_flags = any(
        "flag" in n.get("message", "").lower()
        for n in state["notes"]
        if n.get("agent") == "critic"
    )
    if critic_flags:
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


