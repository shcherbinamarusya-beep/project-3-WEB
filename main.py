from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import random


db = SQLAlchemy()

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    answers = db.Column(db.JSON) 
    correct_answer = db.Column(db.String(255), nullable=False)
    question_type = db.Column(db.String(10), nullable=False)
    city_name = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float) # на всякий если дисон будет плох

class Session(db.Model):
    __tablename__ = 'sessions'
    
    user_id = db.Column(db.String(50), primary_key=True)
    score = db.Column(db.Integer, default=0)
    current_question_index = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, nullable=False)
