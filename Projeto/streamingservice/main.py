from flask import Flask, request, jsonify
from flask_cors import CORS
from shared.shared_config import videos_collection, AWS_S3_BUCKET, s3_client
import logging

app = Flask(__name__)
CORS(app)  # Permitir CORS para todas as rotas

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

try:
    videos_collection.find_one()
    app.logger.info("Conectado à MongoDB com sucesso")
except Exception as e:
    app.logger.error(f"Erro ao conectar à MongoDB: {e}")

@app.route('/api/selected', methods=['GET'])
def selected_Video():
    try:
        title = request.json.get('title')
        
        if not title:
            return jsonify({"error": "Invalid input"}), 400
        
        for video in videos_collection:
            if video('title') == title:
                thumbnailurl = video('thumbnailurl')
                videourl = video('videourl')
                description = video('description')
                duration = video('duration')
        
        response = {
        "title": title,
        "thumbnailurl": thumbnailurl,
        "videourl": videourl,
        "description": description,
        "duration": duration
        }

        return jsonify(response)
            
    except Exception as e:
        app.logger.error(f"Erro na seleção do video")
        return jsonify({'status': 'error', 'message': 'Erro interno do servidor'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=False)