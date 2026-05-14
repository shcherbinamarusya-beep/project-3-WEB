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
