# webcam_snapshot_bot.py
# Скрипт запускает веб-сервер, принимает GET-запрос и автоматически делает снимок с веб-камеры
# без отображения страницы, затем отправляет его в Telegram через Bot API.

from flask import Flask, jsonify
import os
import cv2
import tempfile
import requests


# Настройки Telegram
TELEGRAM_TOKEN = '436156305:AAEcPVHmCWnTKOCopoXKrn6ky9Od-gzTE-o'
CHAT_ID = '337932167'

app = Flask(__name__)

# Функция отправки фото
def send_photo(photo_path):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto'
    with open(photo_path, 'rb') as f:
        files = {'photo': f}
        data = {'chat_id': CHAT_ID}
        return requests.post(url, data=data, files=files).json()

# Маршрут для снимка
@app.route(f'/snapshot', methods=['GET'])
def snapshot():
    # Захват с веб-камеры
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return jsonify({'error': 'Cannot open webcam'}), 500

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return jsonify({'error': 'Capture failed'}), 500

    # Сохранение снимка во временный файл
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        cv2.imwrite(tmp.name, frame)
        tmp_path = tmp.name

    # Отправка в Telegram
    result = send_photo(tmp_path)
    os.remove(tmp_path)

    return jsonify({'telegram_response': result})

if __name__ == '__main__':
    print(f"URL для снимка: http://0.0.0.0:5000/snapshot")
    app.run(host='0.0.0.0', port=5000)
