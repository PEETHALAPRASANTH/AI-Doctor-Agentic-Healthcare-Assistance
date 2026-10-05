from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from langchain_core.messages import HumanMessage, AIMessage

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
        # ---------------------------------------------------------
        # 1. Load previous conversation history
        # ---------------------------------------------------------

        previous_conversations = (
            db.query(Conversation)
            .filter(
                Conversation.user_id == request.user_id
            )
            .order_by(
                Conversation.id.asc()
            )
            .all()
        )

        messages = []

        for conversation in previous_conversations:

            if conversation.role == "user":
                messages.append(
                    HumanMessage(
                        content=conversation.message
                    )
                )

            elif conversation.role == "assistant":
                messages.append(
                    AIMessage(
                        content=conversation.message
                    )
                )

        # ---------------------------------------------------------
        # 2. Add CURRENT user message
        # ---------------------------------------------------------

        messages.append(
            HumanMessage(
                content=request.message
            )
        )

        # ---------------------------------------------------------
        # 3. Send complete conversation to LangGraph
        # ---------------------------------------------------------

        result = agent_graph.invoke(
            {
                "user_id": request.user_id,

                # Latest question
                "question": request.message,

                # IMPORTANT:
                # This contains previous conversation + current message
                "messages": messages,

                "tool_results": [],
                "sources": [],
                "steps": 0,
            }
        )

        # ---------------------------------------------------------
        # 4. Get AI response
        # ---------------------------------------------------------

        answer = result.get(
            "final_answer",
            ""
        )

        if not answer:
            answer = (
                "I was unable to generate a response. "
                "Please try again."
            )

        # ---------------------------------------------------------
        # 5. Get urgent status
        # ---------------------------------------------------------

        urgent = bool(
            result.get(
                "urgent",
                False
            )
        )

        # ---------------------------------------------------------
        # 6. Get sources
        # ---------------------------------------------------------

        sources = list(
            dict.fromkeys(
                result.get(
                    "sources",
                    []
                )
            )
        )

        # ---------------------------------------------------------
        # 7. Save USER message
        # ---------------------------------------------------------

        db.add(
            Conversation(
                user_id=request.user_id,
                role="user",
                message=request.message,
            )
        )

        # ---------------------------------------------------------
        # 8. Save AI response
        # ---------------------------------------------------------

        db.add(
            Conversation(
                user_id=request.user_id,
                role="assistant",
                message=answer,
            )
        )

        db.commit()

        # ---------------------------------------------------------
        # 9. Return response to frontend
        # ---------------------------------------------------------

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
            detail=(
                f"AI service error: "
                f"{type(exc).__name__}: {str(exc)}"
            ),
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
        .filter(
            DemoPatient.user_id == user_id
        )
        .first()
    )

    if patient is None:

        patient = DemoPatient(
            user_id=user_id,
            name="Demo Patient",
            age=28,
            notes=(
                "Synthetic demo patient. "
                "Do not use real medical data."
            ),
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
            detail=(
                f"RAG rebuild failed: "
                f"{type(exc).__name__}: {str(exc)}"
            ),
        )