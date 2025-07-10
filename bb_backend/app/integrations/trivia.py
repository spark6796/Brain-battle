import requests
from ..models.game import Question
import random
import json
from base64 import b64decode

def get_question(categories_id_options: list) -> Question:
    question_obj: Question = {}
    random_id = random.choice(categories_id_options)
    url = f"https://opentdb.com/api.php?amount=1&category={random_id}&type=multiple&encode=base64" 
    response = requests.get(url)
    if response.status_code == 200:
        content = json.loads(response.content)
        question_obj['question'] = b64decode(content['results'][0]['question']).decode()
        question_obj['correct_answer'] = b64decode(content['results'][0]['correct_answer']).decode()
        question_obj['incorrect_answers'] = [b64decode(ans).decode() for ans in content['results'][0]['incorrect_answers']]
        return question_obj