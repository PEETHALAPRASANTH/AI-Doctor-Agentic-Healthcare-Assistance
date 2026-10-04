from typing import Annotated, TypedDict
from operator import add

from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):

    user_id: str

    question: str

    messages: Annotated[list, add_messages]

    tool_results: Annotated[list[str], add]

    sources: Annotated[list[str], add]

    urgent: bool

    final_answer: str

    steps: int