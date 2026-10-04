from langgraph.graph import StateGraph, START, END

from .state import AgentState
from .nodes import (
    safety_node,
    urgent_node,
    call_model,
    execute_tools,
    validate_node,
    should_use_tools,
)


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("safety", safety_node)
    graph.add_node("urgent", urgent_node)
    graph.add_node("model", call_model)
    graph.add_node("tools", execute_tools)
    graph.add_node("validate", validate_node)

    graph.add_edge(START, "safety")

    graph.add_conditional_edges(
        "safety",
        lambda state: "urgent" if state.get("urgent") else "model",
        {
            "urgent": "urgent",
            "model": "model",
        },
    )

    graph.add_edge("urgent", END)

    graph.add_conditional_edges(
        "model",
        should_use_tools,
        {
            "tools": "tools",
            "validate": "validate",
        },
    )

    graph.add_edge("tools", "model")
    graph.add_edge("validate", END)

    return graph.compile()


agent_graph = build_graph()
