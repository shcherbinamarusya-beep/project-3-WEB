import json
import random
from models import Question, Session


class GameLogic:

    CORRECT_PHRASES = [
        'Правильно! Ты настоящий знаток Marvel! ✅',
        'Верно! Щит Капитана Америки одобряет! ✅',
        'Отлично! Тони Старк гордится тобой! ✅',
        'Точно! Тор доволен! ✅',
        'Правильно! Доктор Стрэндж уже это знал! ✅',
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
        user_norm = user_input.strip().lower()
        return any(user_norm == ans.strip().lower() for ans in possible)

    @classmethod
    def get_correct_feedback(cls) -> str:
        return random.choice(cls.CORRECT_PHRASES)

    @classmethod
    def get_wrong_feedback(cls, correct_answer: str) -> str:
        phrase = random.choice(cls.WRONG_PHRASES)
        return phrase.format(answer=correct_answer)
