from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

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

@app.route('/api/stream/', methods=['GET'])
def stream_video():
    try:
        title = request.args.get('title')
        thumbnail = request.args.get('thumbnail')
        description = request.args.get('description')
        duration = request.args.get('duration')

        videos = list(videos_collection.find({}))

        # Initialize video as None before the loop
        video = None  

        for v in videos:  # Rename to avoid confusion
            if title == v['title'] and thumbnail == v['thumbnail'] and description == v['description'] and duration == v['duration']:
                video = v
                break

        if video:  # Check if video was found
            mp4_filename = video['video']
            mp4_url = f"/api/videos/{mp4_filename}"
            return jsonify({
                "mp4_url": mp4_url,
                "title": video['title'],
                "description": video['description'],
                "duration": video['duration']
            })
        else:
            return jsonify({"error": "video nao encontrado"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    




def get_video(filename):
    video_folder = "/Storage/Videos"
    return send_from_directory(video_folder, filename)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
