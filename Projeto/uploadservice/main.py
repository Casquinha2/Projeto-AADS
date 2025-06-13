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
        
        # Verificação dos dados obrigatórios
        if not title or not thumbnailfile or not videofile:
            return jsonify({
                "status": "error",
                "message": f"Dados não fornecidos. Title: {title}, Description: {description}"
            }), 400

        # Define caminhos absolutos baseados no diretório atual
        video_folder = "/Storage/Videos"
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
        
        # Verificando se o arquivo de vídeo foi salvo corretamente
        if not os.path.exists(video_path):
            raise Exception("O arquivo de vídeo não foi salvo.")
        
        # Opcional: Verifica se o arquivo possui um tamanho válido
        if os.path.getsize(video_path) <= 0:
            raise Exception("O arquivo de vídeo foi salvo vazio.")
        
        # Obtém a duração do vídeo
        duration = get_video_duration(video_path)

        if duration is None:
            app.logger.warning("Não foi possível determinar a duração do vídeo.")
            duration = "N/D"
        
        # Insere os dados na base de dados
        videos_collection.insert_one({
            "title": title,
            "thumbnail": thumbnailfile.filename,
            "video": videofile.filename,
            "description": description,
            "duration": duration,
            "views": 0
        })

        app.logger.info("Upload realizado com sucesso!")
        # Resposta para o frontend informando sucesso e a duração do vídeo
        return jsonify({
            "status": "success",
            "message": "Upload realizado com sucesso!",
            "duration": duration
        })

    except Exception as e:
        # Em vez de apenas registrar o erro, você o envia para o cliente
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
        
        # Consulta o vídeo no banco de dados
        try:
            video = videos_collection.find_one(ObjectId(videoId))
            if video is None:
                raise Exception
        except:
            return jsonify({
                'status': 'error',
                'message': f'Vídeo com id: {videoId} não encontrado'
            })

        # Se não houver dados para atualizar, retorna um erro
        if not title and not thumbnailfile and not videofile and not description:
            return jsonify({
                "status": "error",
                "message": f"Dados não fornecidos. Title: {title}, Description: {description}"
            }), 400

        # Inicializa a variável 'duration' com o valor atual salvo no vídeo
        duration = video.get('duration')
        
        # Se um novo thumbnail for enviado, salve-o
        if thumbnailfile:
            thumb_folder = "/Storage/Thumbnails"
            os.makedirs(thumb_folder, exist_ok=True)
            thumb_path = os.path.join(thumb_folder, thumbnailfile.filename)
            app.logger.info(f"Tentando salvar thumbnail em: {thumb_path}")
            thumbnailfile.save(thumb_path)
        
        # Se um novo vídeo for enviado, salve-o e atualize a duração
        if videofile:
            video_folder = "/Storage/Videos"
            os.makedirs(video_folder, exist_ok=True)
            video_path = os.path.join(video_folder, videofile.filename)
            app.logger.info(f"Tentando salvar vídeo em: {video_path}")
            videofile.save(video_path)
            duration = get_video_duration(video_path)
        
        # Use os dados antigos caso os novos campos estejam vazios
        if title == "":
            title = video['title']
        if description == "":
            description = video['description']

        # Atualiza o banco de dados, usando os nomes dos arquivos se novos foram enviados
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