from fastapi import HTTPException, Request, APIRouter
from ..utils import generate_session_key
from ..config import valid_pfps
from datetime import datetime
from ..services.session import SessionManager
import random

router = APIRouter()

@router.post("/get_session")
async def get_session(request: Request):
    try:
        data = await request.json()
        name = data['username'][:11]
        pfp = data['current_pfp']
        if pfp not in valid_pfps:
            pfp = random.choice(valid_pfps)
        session_id = generate_session_key()
        my_data = {
            'name': name,
            'pfp': pfp,
            'in_game': False,
            'created_at': datetime.now()
        }
        SessionManager(session_id).add(**my_data)
        return {"success": "true", "sessionid": session_id}   

    except:
        raise HTTPException(status_code=403, detail="Invalid Request")