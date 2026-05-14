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

