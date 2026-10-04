from langchain_core.messages import SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from .state import AgentState
from .tools import (
    calculate_bmi,
    demo_patient_lookup,
    medical_knowledge_search,
    is_potentially_urgent,
)
from ..config import get_settings



TOOLS = [
    medical_knowledge_search,
    calculate_bmi,
    demo_patient_lookup,
]

TOOL_MAP = {tool.name: tool for tool in TOOLS}



DOCTOR_SYSTEM_PROMPT = """You are an AI Healthcare Assistant designed to provide safe, helpful, and educational health information.

Your primary responsibility is to understand the user's CURRENT message and provide a relevant response. Never ignore the user's question and never return a generic greeting when the user has asked a specific health-related question.

## Core Behavior

1. Always analyze the user's latest message.
2. Answer the actual question asked by the user.
3. Use previous conversation context when it is relevant.
4. Do not assume that every user message is the same.
5. If the user describes symptoms, identify the possible causes or categories that may be relevant, but do not provide a definitive diagnosis.
6. Ask relevant follow-up questions when important information is missing.
7. Provide practical, evidence-based general health information.
8. Clearly distinguish between general information and medical diagnosis.
9. Do not invent medical facts, medications, test results, or patient information.
10. If the user asks something unrelated to healthcare, politely explain that you are primarily designed for healthcare assistance.

## Symptom Assessment

When a user describes symptoms, consider:

* Main symptom
* Location
* Duration
* Severity
* Onset
* Possible triggers
* Associated symptoms
* Relevant medical history
* Current medications, when provided
* Age or other relevant information, when provided

For example, if the user says:

"I have shoulder pain."

Do NOT respond with:

"How can I assist you today with your health concerns?"

Instead, provide useful initial guidance and ask appropriate follow-up questions, such as:

* When did the shoulder pain start?
* Did it happen after an injury or exercise?
* Is the pain in the front, side, or back of the shoulder?
* Does movement make it worse?
* Is there swelling, weakness, numbness, or tingling?
* Are you experiencing chest pain, shortness of breath, sweating, dizziness, or pain spreading to the arm or jaw?

## Emergency Situations

If the user's symptoms could indicate a medical emergency, clearly advise them to seek immediate emergency medical care.

Examples include symptoms such as:

* Severe difficulty breathing
* Severe chest pain or pressure
* Signs of stroke
* Loss of consciousness
* Severe uncontr
"""



def get_llm():
    settings = get_settings()

    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        temperature=0,
        base_url="https://openrouter.ai/api/v1",
    ).bind_tools(
        TOOLS,
        tool_choice="auto",
    )




def safety_node(state: AgentState) -> AgentState:

    question = state["question"]

    return {
        "urgent": is_potentially_urgent(question),
        "steps": state.get("steps", 0) + 1,
    }




def call_model(state: AgentState) -> AgentState:

   
    llm = get_llm()

    messages = [
        SystemMessage(content=DOCTOR_SYSTEM_PROMPT),
        *state.get("messages", []),
    ]

 
    response = llm.invoke(messages)

    return {
        "messages": [response],
        "steps": state.get("steps", 0) + 1,
    }




def urgent_node(state: AgentState) -> AgentState:

    return {
        "final_answer": (
            "Your message contains symptoms that may require urgent "
            "medical attention. This AI assistant cannot determine the "
            "cause or severity. Please contact a qualified healthcare "
            "professional or your local emergency service immediately, "
            "especially if symptoms are severe, rapidly worsening, "
            "or you feel unsafe."
        ),
        "steps": state.get("steps", 0) + 1,
    }




def execute_tools(state: AgentState) -> AgentState:

    messages = state.get("messages", [])

    if not messages:
        return {
            "steps": state.get("steps", 0) + 1
        }

    last = messages[-1]

    results = []
    sources = []
    tool_messages = []

    for call in getattr(last, "tool_calls", []):

        name = call["name"]
        args = call.get("args", {})

        tool = TOOL_MAP.get(name)

        if tool is None:

            result = f"Tool '{name}' is not allowed."

        else:

            try:

                result = str(
                    tool.invoke(args)
                )

                if name == "medical_knowledge_search":
                    sources.append(
                        "local medical knowledge base"
                    )

            except Exception as exc:

                result = (
                    f"Tool '{name}' failed safely: "
                    f"{type(exc).__name__}: {str(exc)}"
                )

        results.append(result)

        tool_messages.append(
            ToolMessage(
                content=result,
                tool_call_id=call["id"],
            )
        )

    return {
        "messages": [last, *tool_messages],
        "tool_results": results,
        "sources": sources,
        "steps": state.get("steps", 0) + 1,
    }



def validate_node(state: AgentState) -> AgentState:

    answer = state.get(
        "final_answer",
        ""
    ).strip()

    if not answer:

        messages = state.get(
            "messages",
            []
        )

        if messages:

            last = messages[-1]

            if hasattr(last, "content") and last.content:

                answer = last.content

        if not answer:

            answer = (
                "I could not generate a response. "
                "Please try again or consult a qualified "
                "healthcare professional."
            )

    return {
        "final_answer": answer,
        "steps": state.get("steps", 0) + 1,
    }



def should_use_tools(state: AgentState) -> str:

    settings = get_settings()

    if (
        state.get("steps", 0)
        >= settings.max_agent_steps
    ):
        return "validate"

    messages = state.get(
        "messages",
        []
    )

    if not messages:
        return "validate"

    last = messages[-1]

    if getattr(
        last,
        "tool_calls",
        None,
    ):
        return "tools"

    return "validate"