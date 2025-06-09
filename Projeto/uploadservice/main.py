import os

from flask import Flask, request, jsonify, send_from_directory
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

        # Define caminhos absolutos baseados no diretório atual
        video_folder =  "/Storage/Videos"
        thumb_folder = "/Storage/Thumbnails"

        # Cria os diretórios se não existirem
        os.makedirs(video_folder, exist_ok=True)
        os.makedirs(thumb_folder, exist_ok=True)

        # Define os caminhos de salvamento
        video_path = os.path.join(video_folder, videofile.filename)
        thumb_path = os.path.join(thumb_folder, thumbnailfile.filename)
        
        app.logger.info(f"Tentando salvar vídeo em: {video_path}")
        app.logger.info(f"Tentando salvar thumbnail em: {thumb_path}")

        # Salva os arquivos
        videofile.save(video_path)
        thumbnailfile.save(thumb_path)
        
        # Obtém a duração do vídeo
        duration = get_video_duration(video_path)
        
        # Insere os dados na base de dados
        videos_collection.insert_one({
            "title": title,
            "thumbnail": thumbnailfile.filename,  # Apenas o nome do arquivo
            "video": videofile.filename,            # Se preferir, só o nome
            "description": description,
            "duration": duration
        })


        return jsonify({
            "status": "success",
            "message": "Upload realizado com sucesso!",
            "duration": duration
        })

    except Exception as e:
        # Em vez de apenas registrar o erro, você também pode enviá-lo para o cliente
        return jsonify({
            "status": "error",
            "message": f"Erro ao processar o upload: {str(e)}"
        }), 500



@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})


def get_video_duration(video_path):
    try:
        with VideoFileClip(video_path) as clip:
            duration = clip.duration
            minutes = int(duration // 60)
            seconds = int(duration % 60)
        return f"{minutes}:{seconds}"
    except Exception as e:
        print(f"Error retrieving video duration: {e}")
        return None



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)