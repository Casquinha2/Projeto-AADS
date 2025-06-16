import os
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
from pymongo import DESCENDING, ASCENDING, ReturnDocument

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


@app.route('/api/video', methods=['GET'])
def show_videos():
    try:
        # Busca todos os documentos sem projeção, ou seja, todos os campos
        videos = list(
            videos_collection
                .find({})
                .sort([('views', DESCENDING), ('title', ASCENDING)])
            )


        app.logger.info(f"Videos na Base de Dados: {videos_collection.find({})}")
        app.logger.info(f"Videos na variavel videos: {videos}")

        # Converte o campo _id para string em cada documento
        for video in videos:
            video['_id'] = str(video['_id'])
            
        app.logger.info(f"Resultados enviados: {videos}")
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


@app.route('/api/thumbnails/<path:filename>', methods=['GET'])
def get_thumbnail(filename):
    thumb_folder = "/Storage/Thumbnails"
    response = send_from_directory(thumb_folder, filename)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response



@app.route('/api/views/<string:videoId>', methods=['POST'])
def inc_views(videoId):
    app.logger.info(f"Recebido videoId para incrementar views: {videoId}")
    try:
        obj_id = ObjectId(videoId)
    except Exception as e:
        app.logger.error(f"ID inválido: {videoId} | Erro: {e}")
        return jsonify({'status': 'error', 'message': 'ID inválido'}), 400

    result = videos_collection.find_one_and_update(
        {'_id': obj_id},
        {'$inc': {'views': 1}},
        return_document=ReturnDocument.AFTER
    )

    app.logger.info(f"Documento após update: {result}")


    if not result:
        app.logger.warning(f"Vídeo não encontrado para o ID: {videoId}")
        return jsonify({'status': 'error', 'message': 'Vídeo não encontrado'}), 404

    app.logger.info(f"Views atualizadas com sucesso para {videoId}: {result['views']}")
    return jsonify({
        'status': 'success',
        'videoId': videoId,
        'views': result['views']
    })



@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
