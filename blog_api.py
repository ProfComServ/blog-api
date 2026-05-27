import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    # Игнорируем всё, просто возвращаем ok
    return jsonify({"status": "ok", "message": "Test mode"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
