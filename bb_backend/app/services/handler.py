from ..services.game import GameManager
from ..services.session import SessionManager
from fastapi import WebSocket
from datetime import timedelta, datetime
import asyncio


async def game_round_loop(game: GameManager,):
    while game.exists():
        if game.started():
            seconds = 35
            current_round = game.get_round()
            if current_round == 1:
                seconds = 41
            current_time = datetime.now()
            time_delta = timedelta(seconds=seconds)
            if ((current_time - game.get_round_start_time()) > time_delta) or (len(game.turn_left()) == 0):
                await game.end_round()
                await asyncio.sleep(3)
                await game.start_round()
        await asyncio.sleep(1)

async def websocket_message_loop(game: GameManager, websocket: WebSocket, session_id: str) -> None:
    
    while game.exists() and SessionManager(session_id).is_legit():

        data = await websocket.receive_json()
        sender_session = data.get('session')
        if sender_session != session_id:
            continue
        if game.is_leader(session_id) and not game.started():
            if data.get('start_game'):
                await game.start()
            elif data.get('kick'):
                userid = data.get('kick')
                session = game.get_session(userid)
                kicked_socket = game.get_socket(session)
                all_sockets = game.get_all_sockets()
                all_sockets.remove(kicked_socket)
                await game.send_all_sockets({'action':'kick'},all_sockets)
                await game.remove_session(session)
            elif data.get('category_change'):
                new_categories = data.get('category_change')
                await game.update_categories(new_categories)


        elif game.started():
            userid = game.get_userid(session_id)
            if userid in game.turn_left():
                answer = data.get('answer')
                game.evaluate_answer(session_id,answer)
                game.turn_completed(userid)
                await game.send_all_sockets({'action':'selected','selected':userid})


