from datetime import datetime
import random
from ..state import games
from ..config import categories, max_rounds
from fastapi import WebSocket, WebSocketDisconnect
from ..services.session import SessionManager
from ..integrations.trivia import get_question

class GameManager:
    def __init__(self, game_id: str) -> None:
        self.game_id = game_id

    def create_game(self, **kwargs: dict) -> None:
        games[self.game_id] = kwargs

    def exists(self) -> bool:
        return self.game_id in games

    def get_points(self, session: str) -> int:
        return games[self.game_id]['sessions'][session]['points']

    def get_round(self) -> int:
        return games[self.game_id]['round']

    def get_round_start_time(self) -> datetime:
        return games[self.game_id]['round_start_time']

    def get_category_ids(self,categories_name: list) -> list:
        id_list = []
        for category in categories_name:
            id_list.append(categories[category])
        return id_list

    async def send_questions(self, categories: list) -> None:
        question = get_question(categories)
        games[self.game_id]['current_question'] = question
        games[self.game_id]['round_start_time'] = datetime.now()
        options = question['incorrect_answers']
        options.append(question['correct_answer'])
        random.shuffle(options)
        data = {
            'action':'question',
            'round':self.get_round(),
            'question':question['question'],
            'options':options
        }
        await self.send_all_sockets(data)

    def add_point(self, session: str, amount: int) -> None:
        games[self.game_id]['sessions'][session]['points']+=amount

    async def end_round(self) -> None:
        correct_answer = games[self.game_id]['current_question']['correct_answer']
        points = {}
        data = {
            'action':'round_end',
            'correct_answer':correct_answer,
            'points':points
            }    
        for session in games[self.game_id]['sessions']:
            points[self.get_userid(session)] = {
                'points':self.get_points(session)
             }
        await self.send_all_sockets(data)
        self.reset_turns()
    
    def remove_game(self) -> None:
        for session in self.all_sessions():
            SessionManager(session).remove()

        del games[self.game_id]

    def turn_completed(self, userid: str):
        games[self.game_id]['round_turn_left'].remove(userid)

    def evaluate_answer(self, session: str, answer: str):
        correct_answer = games[self.game_id]['current_question']['correct_answer']
        if correct_answer == answer:
            self.add_point(session,1)

    def turn_left(self) -> list:
        return games[self.game_id]['round_turn_left']

    def reset_turns(self) -> None:
        user_ids = []
        for session in games[self.game_id]['sessions']:
            user_ids.append(self.get_userid(session))
        games[self.game_id]['round_turn_left'] = user_ids
            
    def get_enabled_categories_id(self) -> list:
        final_list = []
        categories_dict = self.get_categories()
        for category in categories_dict:
            if categories_dict[category]:
                final_list.append(category)
        return self.get_category_ids(final_list)


    async def start_round(self) -> None:
        games[self.game_id]['round']+=1
        if self.get_round() > max_rounds:
            await self.end_game() 
            return
        
        await self.send_questions(self.get_enabled_categories_id())

    def get_categories(self) -> dict:
        return games[self.game_id]['categories']

    async def start(self) -> None:
        games[self.game_id]['started'] = True
        self.reset_turns()
        await self.start_round()

    def started(self) -> bool:
        return games[self.game_id]['started']

    def session_in_game(self, session_id: str) -> bool:
        return session_id in games[self.game_id]['sessions']
    
    def is_leader(self, session_id) -> bool:
        return games[self.game_id]['sessions'][session_id]['leader']

    def all_sessions(self) -> dict:
        return games[self.game_id]['sessions']

    def is_full(self) -> bool:
        return len(games[self.game_id]['sessions']) == 5

    def get_socket(self, session: str) -> WebSocket:
        return games[self.game_id]['sessions'][session]['socket']

    def get_session(self, userid: str) -> str:
        all_sessions = self.all_sessions()
        for session in all_sessions:
            if all_sessions[session]['userid'] == userid:
                return session
        return None

    async def end_game(self) -> None:
        data = {
            'action':'end',
        }
        await self.send_all_sockets(data)
        for session in self.all_sessions():
            SessionManager(session).remove()

        del games[self.game_id]
    
    async def update_categories(self, data: dict) -> None: 

        final_categories = {}
        
        for category in data:
            if category in categories:
                final_categories[category] = data[category]
        games[self.game_id]['categories'] = final_categories
        data = {
            'action':'category_update',
            'categories':final_categories
        }
        await self.send_all_sockets(data)

    async def remove_session(self, session_id: str) -> None:
        userid = self.get_userid(session_id)
        del games[self.game_id]['sessions'][session_id]
        if self.started():
           if len(games[self.game_id]['sessions']) == 0:
               del games[self.game_id]
           else:
            self.turn_completed(userid)
            await self.send_all_sockets({'action':'left','userid':userid})  
        else:
          await self.send_all_sockets({'action':'left','userid':userid})
        SessionManager(session_id).remove()


    async def send_all_sockets(self, data: dict, except_wsocket: list = []) -> None:
        for socket in self.get_all_sockets():
            
            if socket in except_wsocket: continue
            try:
                await socket.send_json(data)
            except WebSocketDisconnect:
                for session in self.all_sessions():
                    if games[self.game_id]['sessions'][session]['socket'] == socket: 
                        await self.remove_session(session)
                        return

    def update_session(self, session_id: str, **kwargs: dict) -> None:
        for name, value in kwargs.items():
            games[self.game_id]['sessions'][session_id][name] = value
     
    def get_userid(self, session_id: str) -> str:
        return games[self.game_id]['sessions'][session_id]['userid']

    def get_leader(self) -> str:
        for session in self.all_sessions():
            if games[self.game_id]['sessions'][session]['leader']:
                return session
            
    def get_profiles(self, session_id: str) -> dict:
        self_userid = self.get_userid(session_id)
        my_data = {
            'action':'self_joined',
            'players':{},
            'self_userid':self_userid,
            'categories':self.get_categories(),
            'game_id':self.game_id,
            'leader':self.get_userid(self.get_leader())
            }
        for session in games[self.game_id]['sessions']:
            userid = self.get_userid(session)
            my_data['players'][userid] = {
             'pfp':SessionManager(session).get_pfp(),
             'name':SessionManager(session).get_name(),
             'points':0
             }
        return my_data
    
    def add_session(self, session_id: str, **kwargs: dict) -> None:
        games[self.game_id]['sessions'][session_id] = {}
        for key, value in kwargs.items():
            games[self.game_id]['sessions'][session_id][key] = value

    def get_all_sockets(self) -> list[WebSocket]:
        return [games[self.game_id]['sessions'][x]['socket'] for x in games[self.game_id]['sessions'] if games[self.game_id]['sessions'][x]['socket']]
    
    def get_game_id(session_id: str) -> str | None:
            try:
                return [x for x in games if session_id in games[x]['sessions'].keys()][0]
            except:
                return None   


