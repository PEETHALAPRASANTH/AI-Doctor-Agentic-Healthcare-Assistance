from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    user_id: str = Field(default="demo-user", min_length=1, max_length=100)


class ChatResponse(BaseModel):
    answer: str
    urgent: bool = False
    sources: list[str] = []


class PatientResponse(BaseModel):
    user_id: str
    name: str
    age: int
    notes: str
