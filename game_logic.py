import json
import random
from models import Question, Session
import re
from difflib import SequenceMatcher

class GameLogic:

    CORRECT_PHRASES = [
        'Правильно! ✅',
        'Верно! ✅',
        'Отлично, это правильный ответ! ✅',
        'Точно! ✅',
        'Да, всё верно! ✅',
    ]

    WRONG_PHRASES = [
        'Неверно! Правильный ответ: {answer} ❌',
        'Не угадал! Было: {answer} ❌',
        'Ошибка! Правильно: {answer} ❌',
        'Мимо! Верный ответ — {answer} ❌',
    ]

    @classmethod
    def start_game(cls, user_session: Session, mode: int):
        """Начать новую игру: выбрать случайные вопросы и обнулить счёт."""
        user_session.mode = mode
        user_session.score = 0
        user_session.current_question_index = 0
        user_session.state = 'playing'

        all_questions = Question.query.all()
        if len(all_questions) <= mode:
            selected = all_questions
        else:
            selected = random.sample(all_questions, mode)

        user_session.set_questions([q.id for q in selected])

    @classmethod
    def get_current_question(cls, user_session: Session):
        question_ids = user_session.get_question_ids()
        idx = user_session.current_question_index

        if idx >= len(question_ids):
            return None

        question_id = question_ids[idx]
        return Question.query.get(question_id)

    @classmethod
    def check_answer(cls, question: Question, user_input: str) -> bool:
        possible = json.loads(question.answers_json)
                user_norm = cls.normalize_answer(user_input)
        return any(cls.answers_match(user_norm, cls.normalize_answer(ans)) for ans in possible)

    @staticmethod
    def normalize_answer(text: str) -> str:
        text = text.lower().replace('ё', 'е')
        text = re.sub(r'[^a-zа-я0-9]+', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @classmethod
    def answers_match(cls, user_answer: str, expected_answer: str) -> bool:
        if not user_answer or not expected_answer:
            return False
        if user_answer == expected_answer:
            return True
        if len(expected_answer) >= 4 and expected_answer in user_answer:
            return True
        if len(user_answer) >= 4 and user_answer in expected_answer:
            return True
        if len(user_answer) >= 5 and len(expected_answer) >= 5:
            return SequenceMatcher(None, user_answer, expected_answer).ratio() >= 0.82
        return False

    @classmethod
    def get_correct_feedback(cls) -> str:
        return random.choice(cls.CORRECT_PHRASES)

    @classmethod
    def get_wrong_feedback(cls, correct_answer: str) -> str:
        phrase = random.choice(cls.WRONG_PHRASES)
        return phrase.format(answer=correct_answer)
