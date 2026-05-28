import os
import ftplib
import logging
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Чтение переменных окружения
FTP_HOST = os.environ.get('FTP_HOST')
FTP_USER = os.environ.get('FTP_USER')
FTP_PASS = os.environ.get('FTP_PASS')
FTP_PATH = os.environ.get('FTP_PATH')
SECRET_TOKEN = os.environ.get('SECRET_TOKEN')

logger.info("Starting API...")
logger.info(f"FTP_HOST: {FTP_HOST}")
logger.info(f"FTP_USER: {FTP_USER}")
logger.info(f"FTP_PATH: {FTP_PATH}")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    # Проверка токена
    token = request.headers.get('X-Auth-Token')
    if not SECRET_TOKEN or token != SECRET_TOKEN:
        logger.warning("Invalid token")
        return jsonify({"status": "error", "message": "Invalid token"}), 403

    # Получение JSON данных
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No JSON data"}), 400

    filename = data.get('filename')
    content = data.get('content')
    if not filename or not content:
        return jsonify({"status": "error", "message": "Missing filename or content"}), 400

    try:
        # Подключение к FTP и загрузка
        with ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS) as ftp:
            ftp.set_pasv(True)
            # Переход в нужную папку
            ftp.cwd(FTP_PATH)
            # Отправка файла: content - это строка, кодируем в байты
            ftp.storbinary(f'STOR {filename}', content.encode('utf-8'))
        logger.info(f"File uploaded: {filename}")
        return jsonify({"status": "ok", "message": f"File {filename} uploaded"}), 200
    except Exception as e:
        logger.error(f"FTP error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
