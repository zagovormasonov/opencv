# webcam_snapshot_bot.py
# Скрипт запускает веб-сервер, принимает HTTP-запрос по ссылке и делает снимок с веб-камеры,
# после чего отправляет его в Telegram-чат через Bot API.

from flask import Flask, jsonify
import cv2
import os
import tempfile
import requests

# 1. Настройки Telegram Bot
TELEGRAM_TOKEN = '436156305:AAEcPVHmCWnTKOCopoXKrn6ky9Od-gzTE-o'  # токен вашего бота
CHAT_ID = '337932167'     # ID чата или пользователя для отправки фото

# 2. Инициализация Flask-приложения
app = Flask(__name__)

# 3. Функция для отправки фото в Telegram
def send_photo_telegram(photo_path: str):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto'
    with open(photo_path, 'rb') as photo_file:
        files = {'photo': photo_file}
        data = {'chat_id': CHAT_ID}
        response = requests.post(url, data=data, files=files)
    return response.json()

# 4. Обработчик HTTP-запроса
@app.route('/snapshot', methods=['GET'])
def snapshot():
    # Открываем первую доступную веб-камеру (0)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return jsonify({'status': 'error', 'message': 'Cannot open webcam'}), 500

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return jsonify({'status': 'error', 'message': 'Failed to capture image'}), 500

    # Сохраняем в временный файл
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        tmp_path = tmp_file.name
        cv2.imwrite(tmp_path, frame)

    # Отправляем через Telegram Bot
    result = send_photo_telegram(tmp_path)

    # Удаляем временный файл
    try:
        os.remove(tmp_path)
    except OSError:
        pass

    # Возвращаем результат
    return jsonify({'status': 'ok', 'telegram_result': result})

# 5. Запуск приложения
if __name__ == '__main__':
    # По умолчанию доступно на http://0.0.0.0:5000/snapshot
    app.run(host='0.0.0.0', port=5000)
