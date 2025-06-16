import os

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId

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
        
        if not title or not thumbnailfile or not videofile:
            return jsonify({
                "status": "error",
                "message": f"Dados não fornecidos. Title: {title}, Description: {description}"
            }), 400

        video_folder = "/Storage/Videos"
        thumb_folder = "/Storage/Thumbnails"

        os.makedirs(video_folder, exist_ok=True)
        os.makedirs(thumb_folder, exist_ok=True)

        video_path = os.path.join(video_folder, videofile.filename)
        thumb_path = os.path.join(thumb_folder, thumbnailfile.filename)
        
        app.logger.info(f"Tentando salvar vídeo em: {video_path}")
        app.logger.info(f"Tentando salvar thumbnail em: {thumb_path}")


        videofile.save(video_path)
        thumbnailfile.save(thumb_path)
        

        if not os.path.exists(video_path):
            raise Exception("O arquivo de vídeo não foi salvo.")

        if os.path.getsize(video_path) <= 0:
            raise Exception("O arquivo de vídeo foi salvo vazio.")

        duration = get_video_duration(video_path)

        if duration is None:
            app.logger.warning("Não foi possível determinar a duração do vídeo.")
            duration = "N/D"
        
        videos_collection.insert_one({
            "title": title,
            "thumbnail": thumbnailfile.filename,
            "video": videofile.filename,
            "description": description,
            "duration": duration,
        })

        app.logger.info(f"Videos na Base de Dados: {videos_collection.find({})}")
        app.logger.info("Upload realizado com sucesso!")
        return jsonify({
            "status": "success",
            "message": "Upload realizado com sucesso!",
            "duration": duration
        })

    except Exception as e:
        app.logger.error(f"Erro ao processar o upload: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Erro ao processar o upload: {str(e)}"
        }), 500



@app.route('/health', methods = ['GET'])
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
    

@app.route('/api/edit', methods=['POST'])
def edit_video():
    try:
        videoId = request.form.get('videoId')
        title = request.form.get('title')
        description = request.form.get('description')
        thumbnailfile = request.files.get('thumbnail')
        videofile = request.files.get('video')
        
        try:
            video = videos_collection.find_one(ObjectId(videoId))
            if video is None:
                raise Exception
        except:
            return jsonify({
                'status': 'error',
                'message': f'Vídeo com id: {videoId} não encontrado'
            })

        if not title and not thumbnailfile and not videofile and not description:
            return jsonify({
                "status": "error",
                "message": f"Dados não fornecidos. Title: {title}, Description: {description}"
            }), 400

        duration = video.get('duration')
        
        if thumbnailfile:
            thumb_folder = "/Storage/Thumbnails"
            os.makedirs(thumb_folder, exist_ok=True)
            thumb_path = os.path.join(thumb_folder, thumbnailfile.filename)
            app.logger.info(f"Tentando salvar thumbnail em: {thumb_path}")
            thumbnailfile.save(thumb_path)
        
        if videofile:
            video_folder = "/Storage/Videos"
            os.makedirs(video_folder, exist_ok=True)
            video_path = os.path.join(video_folder, videofile.filename)
            app.logger.info(f"Tentando salvar vídeo em: {video_path}")
            videofile.save(video_path)
            duration = get_video_duration(video_path)
        
        if title == "":
            title = video['title']
        if description == "":
            description = video['description']

        videos_collection.find_one_and_update(
            {"_id": ObjectId(videoId)},
            {"$set": {
                "title": title,
                "thumbnail": thumbnailfile.filename if thumbnailfile else video.get('thumbnail'),
                "video": videofile.filename if videofile else video.get('video'),
                "description": description,
                "duration": duration
            }}
        )
        
        return jsonify({'message': 'A edição foi bem sucedida'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erro: {e}'})
    
    
@app.route('/api/delete/<string:videoId>', methods=['GET'])
def delete_video(videoId):
    try:
        videos_collection.find_one_and_delete({'_id': ObjectId(videoId)})
        return jsonify({'status': 'success', 'message': 'Video apagado com sucesso'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erro: {e}'})


@app.route('/api/videos/<path:filename>', methods=['GET'])
def get_video(filename):
    video_folder = "/Storage/Videos"
    response = send_from_directory(video_folder, filename)
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)