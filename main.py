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
    longitude = db.Column(db.Float)
