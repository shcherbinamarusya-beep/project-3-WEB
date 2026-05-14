import os
import json
import logging
from flask import Flask, request, jsonify
from database import db, init_db
from models import Question, Session
from game_logic import GameLogic
from maps import get_static_map_url
from content import load_questions_from_json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

app = Flask(name)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marvel_quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'marvel-secret-key-2024')


db.init_app(app)

IMAGES = {
    'welcome':    '965417/7aff91b41cff6aba01d2', 
    'correct':    '965417/7aff91b41cff6aba01d3',
    'wrong':      '965417/7aff91b41cff6aba01d4',
    'result':     '965417/7aff91b41cff6aba01d5',
    'marvel':     '965417/7aff91b41cff6aba01d6',
}

SOUNDS = {
    'correct': '<speaker audio="alice-sounds-animals-cat-1.opus">',  # Встроенные звуки Alice
    'wrong':   '<speaker audio="alice-sounds-animals-cat-2.opus">',
    'intro':   '<speaker audio="alice-music-game-1.opus">',
}

def make_response(text, tts=None, end_session=False, buttons=None,
                  image_id=None, image_title=None, image_desc=None,
                  card_type=None, map_url=None):

    response = {
        'text': text,
        'tts': tts or text,
        'end_session': end_session,
    }

    if buttons:
        response['buttons'] = [
            {'title': btn, 'hide': True} for btn in buttons
        ]


    if image_id:
        response['card'] = {
            'type': 'BigImage',
            'image_id': image_id,
            'title': image_title or text[:50],
            'description': image_desc or '',
        }

    return {'response': response, 'version': '1.0'}

def make_image_gallery(items):
    return {
        'type': 'ItemsList',
        'header': {'text': 'Посмотри на карте:'},
        'items': items,
        'footer': {'text': 'Продолжаем игру!'}
    }
    
@app.route('/webhook', methods=['POST'])
def webhook():
    """Основной вебхук для обработки запросов от Яндекс.Алисы."""
    try:
        data = request.get_json()
        logger.info(f"Входящий запрос: {json.dumps(data, ensure_ascii=False)[:200]}")

        # Достаём данные из запроса
        session_data = data.get('session', {})
        user_id = session_data.get('user_id') or session_data.get('application', {}).get('application_id', 'anon')
        is_new_session = session_data.get('new', False)
        request_body = data.get('request', {})
        user_input = request_body.get('original_utterance', '').strip().lower()
        is_ping = request_body.get('type') == 'SimpleUtterance' and user_input == ''

        # Обрабатываем пинг (проверка доступности навыка)
        if is_ping:
            return jsonify(make_response('Навык работает!', end_session=True))

        # Получаем или создаём сессию пользователя
        user_session = Session.get_or_create(user_id)

        # Обрабатываем команды завершения
        if user_input in ('стоп', 'выход', 'закрыть', 'хватит', 'нет', 'не хочу'):
            if user_session.state == 'asking_replay':
                user_session.reset()
                db.session.commit()
                return jsonify(make_response(
                    'Спасибо за игру! До встречи, герой! 🦸',
                    tts='Спасибо за игру! До встречи, герой!',
                    end_session=True,
                    image_id=IMAGES['marvel']
                ))

        # Маршрутизация по состоянию сессии
        if is_new_session or user
[С
_list)}'
        ))

    # Следующий вопрос
    next_question = GameLogic.get_current_question(user_session)
    return ask_question(user_session, next_question, preamble=feedback_text, preamble_tts=feedback_tts)

def handle_replay(user_session, user_input):
    """Обработка запроса на повторную игру."""
    if any(w in user_input for w in ('да', 'ещё', 'еще', 'снова', 'заново', 'хочу', 'играть')):
        user_session.reset()
        db.session.commit()
        return handle_welcome(user_session)
    else:
        user_session.reset()
        db.session.commit()
        return jsonify(make_response(
            'Спасибо за игру! Возвращайся, когда захочешь ещё раз проверить знания! 🦸‍♂️',
            tts='Спасибо за игру! Возвращайся!',
            end_session=True
        ))
    
