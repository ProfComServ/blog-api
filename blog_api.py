import os
import ftplib
import logging
from flask import Flask, request, jsonify

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Чтение переменных окружения
FTP_HOST = os.environ.get('FTP_HOST')
FTP_USER = os.environ.get('FTP_USER')
FTP_PASS = os.environ.get('FTP_PASS')
FTP_PATH = os.environ.get('FTP_PATH')
SECRET_TOKEN = os.environ.get('SECRET_TOKEN')

# Проверка наличия переменных при старте
if not all([FTP_HOST, FTP_USER, FTP_PASS, FTP_PATH, SECRET_TOKEN]):
    logger.error("Missing required environment variables!")
    logger.error(f"FTP_HOST: {FTP_HOST is not None}")
    logger.error(f"FTP_USER: {FTP_USER is not None}")
    logger.error(f"FTP_PASS: {FTP_PASS is not None}")
    logger.error(f"FTP_PATH: {FTP_PATH is not None}")
    logger.error(f"SECRET_TOKEN: {SECRET_TOKEN is not None}")
    # Не выходим, но логируем ошибку – потом увидим в логах
else:
    logger.info("All environment variables are set")

@app.route('/health', methods=['GET'])
def health():
    logger.info("Health check called")
    return jsonify({"status": "ok"}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    token = request.headers.get('X-Auth-Token')
    if not SECRET_TOKEN or token != SECRET_TOKEN:
        logger.warning(f"Invalid token attempt: {token}")
        return jsonify({"status": "error", "message": "Invalid token"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No JSON data"}), 400

    filename = data.get('filename')
    content = data.get('content')
    if not filename or not content:
        return jsonify({"status": "error", "message": "Missing filename or content"}), 400

    try:
        logger.info(f"Uploading file: {filename}")
        with ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS) as ftp:
            ftp.cwd(FTP_PATH)
            ftp.storbinary(f'STOR {filename}', content.encode('utf-8'))
        logger.info(f"Successfully uploaded {filename}")
        return jsonify({"status": "ok", "message": f"File {filename} uploaded"})
    except Exception as e:
        logger.error(f"FTP upload error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
