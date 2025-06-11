import os
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)  # Permitir CORS para todas as rotas

logging.basicConfig(level=logging.DEBUG)

try:
    client = MongoClient('mongodb://admin:password123@mongodb:27017/')
    db = client.videos_db
    videos_collection = db.videos
    app.logger.info("Conectado à MongoDB com sucesso")
except Exception as e:
    app.logger.error(f"Erro ao conectar à MongoDB: {e}")

# Essa função garante que todas as respostas HTML incluam UTF-8 no Content-Type
@app.after_request
def set_charset(response):
    if response.content_type.startswith("text/html"):
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

@app.route('/api/video', methods=['GET'])
def show_videos():
    try:
        videos = list(videos_collection.find({}))
        for video in videos:
            video['_id'] = str(video['_id'])
        app.logger.info(f"Resultados enviados: {videos}")
        # Retorna uma resposta estruturada com status, mensagem e dados
        return jsonify({
            "status": "success",
            "message": "Vídeos carregados com sucesso.",
            "data": videos
        })
    except Exception as e:
        app.logger.error(f"Erro ao obter resultados: {e}")
        return jsonify({
            "status": "error",
            "message": f"Erro ao obter resultados: {str(e)}",
            "data": []
        }), 500

@app.route('/api/thumbnails/<path:filename>')
def get_thumbnail(filename):
    thumb_folder = "/Storage/Thumbnails"
    response = send_from_directory(thumb_folder, filename)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/api/videos/<path:filename>')
def get_video(filename):
    video_folder =  "/Storage/Videos"
    return send_from_directory(video_folder, filename)


@app.route('/api/video/<string:videoId>')
def video_by_id(videoId):
    try:
        # Converte o id de string para ObjectId
        video = videos_collection.find_one({"_id": ObjectId(videoId)})
        if video:
            # Como o ObjectId não é serializável, convertemos ele para string
            video['_id'] = str(video['_id'])
            return jsonify(video)
        else:
            return jsonify({"message": "Nenhum vídeo encontrado com esse id"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
