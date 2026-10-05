from typing import Any
from langchain_core.tools import tool

from ..rag.vectorstore import search_knowledge


URGENT_TERMS = [
    "severe chest pain",
    "chest pain and difficulty breathing",
    "difficulty breathing",
    "can't breathe",
    "cannot breathe",
    "severe bleeding",
    "unconscious",
    "loss of consciousness",
    "stroke symptoms",
    "face drooping",
    "sudden weakness",
    "suicidal",
    "overdose",
]


def is_potentially_urgent(text: str) -> bool:
    normalized = text.lower()
    return any(term in normalized for term in URGENT_TERMS)


@tool
def medical_knowledge_search(query: str) -> str:
    """Search the approved local medical-information knowledge base."""
    docs = search_knowledge(query, k=4)
    if not docs:
        return "No relevant knowledge-base information was found."

    parts = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        parts.append(f"[Source: {source}]\n{doc.page_content}")
    return "\n\n".join(parts)


@tool
def calculate_bmi(weight_kg: float, height_m: float) -> str:
    """Calculate BMI from weight in kilograms and height in meters."""
    if height_m <= 0 or weight_kg <= 0:
        return "Weight and height must be positive values."
    bmi = weight_kg / (height_m ** 2)
    return f"BMI calculation result: {bmi:.1f}. This is an informational calculation, not a diagnosis."


@tool
def demo_patient_lookup(user_id: str) -> str:
    """Return synthetic demo patient data. Never use this tool with real patient data."""
    demo_data = {
        "demo-user": {
            "name": "Demo Patient",
            "age": 28,
            "notes": "Synthetic demo record. No real medical history is stored.",
        },
        "test-user": {from typing import Any

from langchain_core.tools import tool

from ..rag.vectorstore import search_knowledge




URGENT_TERMS = [
    "chest pain",
    "chest pressure",
    "severe chest pain",
    "chest pain and difficulty breathing",

    "difficulty breathing",
    "shortness of breath",
    "can't breathe",
    "cannot breathe",

    "severe bleeding",

    "unconscious",
    "loss of consciousness",

    "stroke symptoms",
    "face drooping",
    "sudden weakness",

    "suicidal",
    "suicide",

    "overdose",
]


def is_potentially_urgent(text: str) -> bool:

    if not text:
        return False

    normalized = text.lower().strip()

    return any(
        term in normalized
        for term in URGENT_TERMS
    )




@tool
def medical_knowledge_search(query: str) -> str:
    """Search the approved local medical-information knowledge base."""

    docs = search_knowledge(
        query,
        k=4
    )

    if not docs:
        return (
            "No relevant knowledge-base "
            "information was found."
        )

    parts = []

    for doc in docs:

        source = doc.metadata.get(
            "source",
            "unknown"
        )

        parts.append(
            f"[Source: {source}]\n"
            f"{doc.page_content}"
        )

    return "\n\n".join(parts)




@tool
def calculate_bmi(
    weight_kg: float,
    height_m: float
) -> str:
    """Calculate BMI from weight in kilograms and height in meters."""

    if height_m <= 0 or weight_kg <= 0:
        return (
            "Weight and height must be "
            "positive values."
        )

    bmi = weight_kg / (height_m ** 2)

    return (
        f"BMI calculation result: {bmi:.1f}. "
        "This is an informational calculation, "
        "not a diagnosis."
    )




@tool
def demo_patient_lookup(user_id: str) -> str:
    """Return synthetic demo patient data. Never use this tool with real patient data."""

    demo_data = {

        "demo-user": {
            "name": "Demo Patient",
            "age": 28,
            "notes": (
                "Synthetic demo record. "
                "No real medical history is stored."
            ),
        },

        "test-user": {
            "name": "Test Patient",
            "age": 35,
            "notes": (
                "Synthetic demo record "
                "for testing only."
            ),
        },
    }

    patient = demo_data.get(
        user_id
    )

    if not patient:

        return (
            "No synthetic demo patient "
            "was found for this user."
        )

    return (
        f"Name: {patient['name']}\n"
        f"Age: {patient['age']}\n"
        f"Notes: {patient['notes']}"
    )
            "name": "Test Patient",
            "age": 35,
            "notes": "Synthetic demo record for testing only.",
        },
    }
    patient = demo_data.get(user_id)
    if not patient:
        return "No synthetic demo patient was found for this user."
    return f"Name: {patient['name']}\nAge: {patient['age']}\nNotes: {patient['notes']}"
