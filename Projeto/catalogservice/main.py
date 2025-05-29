from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from shared.shared_config import videos_collection, AWS_S3_BUCKET, s3_client

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

try:
    videos_collection.find_one()
    app.logger.info("Conectado à MongoDB com sucesso")
except Exception as e:
    app.logger.error(f"Erro ao conectar à MongoDB: {e}")

try:
    s3_client.head_bucket(Bucket=AWS_S3_BUCKET)
    app.logger.info("Connected to S3 bucket successfully!")
except Exception as e:
    app.logger.info(f"Error connecting to S3 bucket: {e}")


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