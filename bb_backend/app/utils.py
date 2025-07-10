import uuid

def generate_game_key() -> str:
    return str(uuid.uuid4()).replace('-', '')[:6]

def generate_session_key() -> str:
    return str(uuid.uuid4())

