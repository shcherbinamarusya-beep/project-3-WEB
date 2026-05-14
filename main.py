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


        if is_new_session or user
[С
_list)}'
        ))

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

def ask_question(user_session, question, first=False, preamble='', preamble_tts=''):
    questions_list = json.loads(user_session.questions_json)
    q_num = user_session.current_question_index + 1
    total = len(questions_list)

    prefix = f'Вопрос {q_num} из {total}. '
    q_text = prefix + question.text

    if preamble:
        full_text = preamble + '\n\n' + q_text
        full_tts = preamble_tts + ' ' + q_text
    else:
        full_text = q_text
        full_tts = (SOUNDS['intro'] if first else '') + q_text

    emoji = '🌍' if question.question_type == 'city' else '🦸'
    full_text = emoji + ' ' + full_text

    return jsonify(make_response(
        full_text,
        tts=full_tts,
        buttons=['Подсказка', 'Пропустить'],
        image_id=IMAGES['marvel']
    ))

def finalize_text(user_session, preamble=''):
    questions_list = json.loads(user_session.questions_json)
    total = len(questions_list)
    score = user_session.score

    if score == total:
        verdict = 'Великолепно! Ты настоящий знаток Marvel! 🏆'
    elif score >= total * 0.7:
        verdict = 'Отлично! Ты хорошо знаешь вселенную Marvel! 👏'
    elif score >= total * 0.4:
        verdict = 'Неплохо! Есть куда расти, герой! 💪'
    else:
        verdict = 'Стоит пересмотреть фильмы Marvel! 🎬'

    result = f'Игра окончена!\nТвой результат: {score} из {total} правильных ответов.\n{verdict}'
    user_session.state = 'asking_replay'
    db.session.commit()

    return (preamble + '\n\n' if preamble else '') + result + '\n\nХочешь сыграть ещё раз?'

def finalize_game(user_session):
    result_text = finalize_text(user_session)
    return jsonify(make_response(
        result_text,
        buttons=['Да, ещё раз!', 'Нет, спасибо'],
        image_id=IMAGES['result']
    ))

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'Marvel Quiz Alice Skill'})

if name == 'main':
    with app.app_context():
        init_db()
        if Question.query.count() == 0:
            load_questions_from_json('questions.json')
            logger.info('Вопросы загружены из questions.json')
        else:
            logger.info(f'В БД уже {Question.query.count()} вопросов')

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)_session.state == 'idle':
            return handle_welcome(user_session)

        elif user_session.state == 'choosing_mode':
            return handle_mode_choice(user_session, user_input)

        elif user_session.state == 'playing':
            return handle_answer(user_session, user_input)

        elif user_session.state == 'asking_replay':
            return handle_replay(user_session, user_input)

        else:
            user_session.state = 'idle'
            db.session.commit()
            return handle_welcome(user_session)

    except Exception as e:
        logger.error(f"Ошибка обработки запроса: {e}", exc_info=True)
        return jsonify(make_response(
            'Произошла ошибка. Попробуй ещё раз!',
            buttons=['Начать заново']
        ))

def handle_welcome(user_session):
    tts_intro = SOUNDS['intro']
    text = (
        'Добро пожаловать в викторину по вселенной Marvel! '
        'Тебя ждут вопросы о героях, злодеях и городах киновселенной. '
        'За каждый правильный ответ — 1 очко. '
        'Выбери режим игры: 5 или 10 вопросов?'
    )
    tts = tts_intro + text

    user_session.state = 'choosing_mode'
    db.session.commit()

    return jsonify(make_response(
        text, tts=tts,
        buttons=['5 вопросов', '10 вопросов'],
        image_id=IMAGES['welcome'],
        image_title='Marvel Quiz',
        image_desc='Проверь свои знания о вселенной Marvel!'
    ))

def handle_mode_choice(user_session, user_input):
    if '10' in user_input or 'десять' in user_input:
        mode = 10
    elif '5' in user_input or 'пять' in user_input:
        mode = 5
    else:
        return jsonify(make_response(
            'Не понял выбор. Скажи "5 вопросов" или "10 вопросов".',
            buttons=['5 вопросов', '10 вопросов']
        ))

    GameLogic.start_game(user_session, mode)
    db.session.commit()

    question = GameLogic.get_current_question(user_session)
    if not question:
        return jsonify(make_response('Не удалось загрузить вопросы. Попробуй позже!'))

    return ask_question(user_session, question, first=True)
def handle_answer(user_session, user_input):
    """Обработка ответа пользователя на вопрос."""
    question = GameLogic.get_current_question(user_session)
    if not question:
        return finalize_game(user_session)

    is_correct = GameLogic.check_answer(question, user_input)

    if is_correct:
        user_session.score += 1
        feedback_text = GameLogic.get_correct_feedback()
        feedback_tts = SOUNDS['correct'] + feedback_text
        img_id = IMAGES['correct']
    else:
        correct_ans = question.correct_answer
        feedback_text = GameLogic.get_wrong_feedback(correct_ans)
        feedback_tts = SOUNDS['wrong'] + feedback_text
        img_id = IMAGES['wrong']

    # Показываем карту для вопросов о городах
    extra_card = None
    map_info = ''
    if question.question_type == 'city' and question.latitude and question.longitude:
        map_url = get_static_map_url(question.latitude, question.longitude, question.city_name)
        if map_url:
            map_info = f'\n🗺️ {question.city_name} на карте!'
            # Для карты используем текстовое описание (Static API — внешняя ссылка)
            feedback_text += f'\n\nГород {question.city_name}: {map_url}'

    # Переходим к следующему вопросу
    user_session.current_question_index += 1
    db.session.commit()

    # Проверяем, есть ли ещё вопросы
    questions_list = json.loads(user_session.questions_json)
    if user_session.current_question_index >= len(questions_list):
        # Игра завершена — показываем фидбек и результат
        result_text = finalize_text(user_session, feedback_text)
        return jsonify(make_response(
            result_text,
            tts=feedback_tts + ' ' + result_text,
            buttons=['Сыграть ещё раз', 'Выйти'],
            image_id=IMAGES['result'],
    
