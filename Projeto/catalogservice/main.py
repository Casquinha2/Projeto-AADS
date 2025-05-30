from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # Permitir CORS para todas as rotas

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

try:
    client = MongoClient('mongodb://admin:password123@mongodb:27017/')
    db = client.videos_db
    videos_collection = db.videos
    app.logger.info("Conectado à MongoDB com sucesso")
except Exception as e:
    app.logger.error(f"Erro ao conectar à MongoDB: {e}")


@app.route('/api/video', methods=['GET'])
def show_videos():
    try:
        # Retrieve all video documents from the collection;
        videos = list(videos_collection.find({}))
        
        app.logger.info(f"Resultados enviados: {videos}")
        return jsonify(videos)
    except Exception as e:
        app.logger.error(f"Erro ao obter resultados: {e}")
        return jsonify({"error": "Erro ao obter resultados"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)