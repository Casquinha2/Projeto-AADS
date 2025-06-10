from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import subprocess

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


@app.route('/api/stream/<string:videoId>')
def stream_video(videoId):
    try:
        # Converte o videoId para ObjectId e busca o documento
        video = videos_collection.find_one({"_id": ObjectId(videoId)})
        if video:
            video_file = f"/Storage/Videos/{video['filename']}"
            streams_folder = "/Storage/Streams"

            hls_url = f"/Storage/Streams/{videoId}.m3u8"
            dash_url = f"/Storage/Streams/{videoId}.mpd"

            if convert_to_hls(video_file, streams_folder) and convert_to_dash(video_file, streams_folder):
                return jsonify({"hls_url": hls_url, "dash_url": dash_url})
            else:
                return jsonify({"message": "Erro na conversão do vídeo"}), 500
            
        else:
            return jsonify({"message": "Nenhum vídeo encontrado com esse id"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500



def convert_to_hls(input_path, output_dir):
    """Convert video to HLS format using FFmpeg"""
    os.makedirs(output_dir, exist_ok=True)

    hls_playlist = os.path.join(output_dir, 'playlist.m3u8')

    # HLS conversion command
    hls_cmd = [
        'ffmpeg', '-i', input_path,
        '-profile:v', 'baseline',
        '-level', '3.0',
        '-start_number', '0',
        '-hls_time', '10',
        '-hls_list_size', '0',
        '-f', 'hls',
        hls_playlist
    ]

    try:
        subprocess.run(hls_cmd, check=True)
        app.logger.info(f"HLS conversion completed for {input_path}")
        return True
    except subprocess.CalledProcessError as e:
        app.logger.error(f"HLS conversion failed: {e}")
        return False
    
def convert_to_dash(input_path, output_dir):
    """Convert video to DASH format using FFmpeg"""
    os.makedirs(output_dir, exist_ok=True)

    dash_playlist = os.path.join(output_dir, 'manifest.mpd')

    # DASH conversion command
    dash_cmd = [
        'ffmpeg', '-i', input_path,
        '-map', '0:v', '-map', '0:a',
        '-c:v', 'libx264', '-x264-params', 'keyint=60:min-keyint=60:no-scenecut=1',
        '-b:v:0', '1500k',
        '-c:a', 'aac', '-b:a', '128k',
        '-bf', '1', '-keyint_min', '60',
        '-g', '60', '-sc_threshold', '0',
        '-f', 'dash',
        '-use_template', '1', '-use_timeline', '1',
        '-init_seg_name', 'init-$RepresentationID$.m4s',
        '-media_seg_name', 'chunk-$RepresentationID$-$Number%05d$.m4s',
        '-adaptation_sets', 'id=0,streams=v id=1,streams=a',
        dash_playlist
    ]

    try:
        subprocess.run(dash_cmd, check=True)
        app.logger.info(f"DASH conversion completed for {input_path}")
        return True
    except subprocess.CalledProcessError as e:
        app.logger.error(f"DASH conversion failed: {e}")
        return False


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)