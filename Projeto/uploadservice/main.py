import os

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from pymongo import MongoClient

from moviepy.editor import VideoFileClip

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

try:
    client = MongoClient('mongodb://admin:password123@mongodb:27017/')
    db = client.videos_db
    videos_collection = db.videos
    app.logger.info("Conectado à MongoDB com sucesso")
except Exception as e:
    app.logger.error(f"Erro ao conectar à MongoDB: {e}")


@app.route('/api/upload', methods=['POST'])
def upload_video():
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        thumbnailfile = request.files.get('thumbnail')
        videofile = request.files.get('video')
        
        # Verificação dos dados obrigatórios
        if not title or not thumbnailfile or not videofile:
            return jsonify({
                "status": "error",
                "message": f"Dados não fornecidos. Title: {title}, Description: {description}"
            }), 400

        # Exemplo de salvamento temporário para obter a duração do vídeo
        video_filename = videofile.filename
        temp_video_path = os.path.join("/tmp", video_filename)
        videofile.save(temp_video_path)
        duration = get_video_duration(temp_video_path)
        os.remove(temp_video_path)

        # Inserção dos dados na base de dados
        videos_collection.insert_one({
            "title": title,
            "thumbnailfile": thumbnailfile.filename,
            "videofile": videofile.filename,
            "description": description,
            "duration": duration
        })

        app.logger.info("Upload concluído com sucesso")
        return jsonify({
            "status": "success",
            "message": "Upload realizado com sucesso!",
            "duration": duration
        })

    except Exception as e:
        app.logger.error(f"Erro durante o upload: {e}")
        return jsonify({
            "status": "error",
            "message": "Erro ao processar o upload."
        }), 500



@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})


def get_video_duration(video_path):
    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration  # duration in seconds

        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        clip.reader.close()       # release the file handle

        # If your movie has audio, you might also want to release the audio resources:
        if clip.audio:
            clip.audio.reader.close_proc()

        return f"{str(minutes)}:{str(seconds)}"
    
    except Exception as e:
        print(f"Error retrieving video duration: {e}")
        return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)