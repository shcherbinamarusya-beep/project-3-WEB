import json
import random
from database import db


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    answers_json = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(200), nullable=False)
    question_type = db.Column(db.String(50), default='marvel')
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    city_name = db.Column(db.String(100), nullable=True)
    hint = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f'<Question id={self.id} text="{self.text[:40]}...">'


class Session(db.Model):
    """Модель игровой сессии пользователя."""
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(200), unique=True, nullable=False, index=True)
    state = db.Column(db.String(50), default='idle')
    score = db.Column(db.Integer, default=0)
    current_question_index = db.Column(db.Integer, default=0)
    questions_json = db.Column(db.Text, default='[]')
    mode = db.Column(db.Integer, default=5)

    def __repr__(self):
        return f'<Session user_id={self.user_id} state={self.state} score={self.score}>'

    @classmethod
    def get_or_create(cls, user_id: str) -> 'Session':
        session = cls.query.filter_by(user_id=user_id).first()
        if not session:
            session = cls(user_id=user_id)
            db.session.add(session)
            db.session.commit()
        return session

    def reset(self):
        self.state = 'idle'
        self.score = 0
        self.current_question_index = 0
        self.questions_json = '[]'
        self.mode = 5

    def set_questions(self, question_ids: list):
        self.questions_json = json.dumps(question_ids)

    def get_question_ids(self) -> list:
        """Получить список ID вопросов текущей игры."""
        return json.loads(self.questions_json)
