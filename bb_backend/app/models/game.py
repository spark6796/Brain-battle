from pydantic import BaseModel


class HostRequest(BaseModel):
    session_id: str
    mode: str
    # categories: list

class JoinRequest(BaseModel):
    session_id: str
    game_id: str

class Question(BaseModel):
    question: str
    correct_answer: str
    incorrect_answers: list