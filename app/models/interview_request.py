from pydantic import BaseModel

class InterviewRequest(BaseModel):
    role: str
    experience_level: str
