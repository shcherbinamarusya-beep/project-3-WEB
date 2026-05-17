import json
import logging
from database import db
from models import Question

logger = logging.getLogger(__name__)


def load_questions_from_json(filepath: str):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error(f'Файл вопросов не найден: {filepath}')
        return
    except json.JSONDecodeError as e:
        logger.error(f'Ошибка парсинга JSON в {filepath}: {e}')
        return

    added = 0
    skipped = 0

    for item in data:
        if not item.get('text') or not item.get('answers_json') or not item.get('correct_answer'):
            logger.warning(f'Пропущен вопрос с неполными данными: {item}')
            skipped += 1
            continue

        exists = Question.query.filter_by(text=item['text']).first()
        if exists:
            skipped += 1
            continue

        question = Question(
            text=item['text'],
            answers_json=item['answers_json'],
            correct_answer=item['correct_answer'],
            question_type=item.get('question_type', 'marvel'),
            latitude=item.get('latitude'),
            longitude=item.get('longitude'),
            city_name=item.get('city_name'),
            hint=item.get('hint'),
        )
        db.session.add(question)
        added += 1

    db.session.commit()
    logger.info(f'Загрузка вопросов завершена: добавлено {added}, пропущено {skipped}.')
