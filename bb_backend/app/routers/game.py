from fastapi import APIRouter
import asyncio
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
import traceback
from ..services.game import GameManager
from ..services.session import SessionManager
from ..services.handler import game_round_loop, websocket_message_loop
from ..utils import generate_game_key, generate_session_key
from ..models.game import HostRequest, JoinRequest
from ..config import categories

router = APIRouter()

@router.websocket("/join_game")
async def join_socket(websocket: WebSocket):
    try:
        await websocket.accept()  
        query_params = websocket.query_params
        session_id = query_params.get('session_id',None)
        
        session_mngr = SessionManager(session_id)
        if not session_mngr.is_legit(): 
            await websocket.close(1000,'Invalid Session')
            return

        game_id = GameManager.get_game_id(session_id)

        if not game_id:
            await websocket.close(1000,"You can't join this game")
            return
        
        game = GameManager(game_id)
        
        if session_id not in game.all_sessions():
            await websocket.close(1000,'You dont belong to this game')
            return

        if game.started():
            await websocket.close(1000,'Game Already started')
            return
        
        session_mngr.join_game()
        
        game.update_session(session_id,
            **{
                'socket':websocket,
            })

        await websocket.send_json(
            game.get_profiles(session_id)
            )

        
        await game.send_all_sockets(
            {
                'action':'joined',
                'userid':game.get_userid(session_id),
                'name':session_mngr.get_name(),
                'pfp':session_mngr.get_pfp()   
            }, 
            [websocket]
        )

        await asyncio.gather(
                game_round_loop(game),
                websocket_message_loop(game, websocket, session_id)
            )

    except WebSocketDisconnect:
        session_id = websocket.query_params.get('session_id')
        if (session_id == game.get_leader()) and not game.started():
            await game.send_all_sockets({'action':'leader_left'},[websocket])
            game.remove_game()
            SessionManager(session_id).remove()
        else:
            await game.remove_session(session_id)
    except Exception as e:
        traceback.print_exc(e)
        await websocket.close()
    

@router.post("/host")
async def host(data: HostRequest):
    try:
        session = SessionManager(data.session_id)
        if not session.is_legit() or session.in_game(): raise

        game_id = generate_game_key()
        
        my_categories = {category: True for category in categories.keys()}
        my_game = {
            'started':False,
            'round':0,
            'categories':my_categories,
            'round_turn_left':[],
            'round_start_time':None,
            'current_question':None,
            'sessions':{
                data.session_id: {
                    'leader': True,
                    'userid':generate_session_key(),
                    'socket':None,
                    'points':0,
                    'pfp':session.get_pfp()
                    },
            }
        }
 
        GameManager(game_id).create_game(**my_game)
        session.join_game()
    except:
        raise HTTPException(status_code=400, detail='Falied to create the game')

@router.post('/join')
async def join_game(data: JoinRequest):
    try:
        session = SessionManager(data.session_id)
        game = GameManager(data.game_id)

        if not game.exists():
            raise HTTPException(status_code=400, detail='Game not found.')
        if game.started():
            raise HTTPException(status_code=400, detail='Game already started.')
        if session.in_game():
            raise HTTPException(status_code=400, detail='Session already in a game.')
        if game.is_full():
            raise HTTPException(status_code=400, detail='Game is full.')
        if not session.is_legit():
            raise HTTPException(status_code=400, detail='Invalid session.')
        
        game.add_session(
            data.session_id,**{
                'name':session.get_name(),
                'leader':False,
                'userid':generate_session_key(),
                'points':0,
                'socket':None,
                'pfp':session.get_pfp()
                }
            )
    except:
        raise HTTPException(status_code=400, detail='Failed To Join.') 