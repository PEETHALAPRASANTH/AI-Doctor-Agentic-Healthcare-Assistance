from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Conversation, DemoPatient
from ..schemas import ChatRequest, ChatResponse, PatientResponse
from ..agents.graph import agent_graph
from ..rag.vectorstore import build_vectorstore


router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ai-doctor-agent",
    }


@router.post("/doctor/chat", response_model=ChatResponse)
def doctor_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    try:
        result = agent_graph.invoke(
            {
                "user_id": request.user_id,
                "question": request.message,
                "messages": [],
                "tool_results": [],
                "sources": [],
                "steps": 0,
            }
        )

        answer = result.get("final_answer", "")
        urgent = bool(result.get("urgent", False))
        sources = list(
            dict.fromkeys(
                result.get("sources", [])
            )
        )

        db.add(
            Conversation(
                user_id=request.user_id,
                role="user",
                message=request.message,
            )
        )

        db.add(
            Conversation(
                user_id=request.user_id,
                role="assistant",
                message=answer,
            )
        )

        db.commit()

        return ChatResponse(
            answer=answer,
            urgent=urgent,
            sources=sources,
        )

    except Exception as exc:
        db.rollback()

        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {type(exc).__name__}: {str(exc)}",
        )


@router.get(
    "/patients/{user_id}",
    response_model=PatientResponse,
)
def get_demo_patient(
    user_id: str,
    db: Session = Depends(get_db),
):
    patient = (
        db.query(DemoPatient)
        .filter(DemoPatient.user_id == user_id)
        .first()
    )

    if patient is None:
        patient = DemoPatient(
            user_id=user_id,
            name="Demo Patient",
            age=28,
            notes="Synthetic demo record. Do not use real patient data.",
        )

        db.add(patient)
        db.commit()
        db.refresh(patient)

    return PatientResponse(
        user_id=patient.user_id,
        name=patient.name,
        age=patient.age,
        notes=patient.notes,
    )


@router.post("/rag/rebuild")
def rebuild_rag():
    try:
        build_vectorstore()

        return {
            "status": "ok",
            "message": "FAISS knowledge index rebuilt.",
        }

    except Exception as exc:
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"RAG rebuild failed: {type(exc).__name__}: {str(exc)}",
        )