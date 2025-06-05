import os

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

from pymongo import MongoClient
import boto3


from moviepy.editor import VideoFileClip

import logging

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

try:
    AWS_S3_BUCKET = 'ualflix'
    s3_client = boto3.client(
        's3',
        aws_access_key_id='AKIARWHN5DKOOJPQ2CVG',
        aws_secret_access_key='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',
        region_name='eu-west-3'
    )
    s3_client.head_bucket(Bucket=AWS_S3_BUCKET)
    app.logger.info("Connected to S3 bucket successfully!")
except Exception as e:
    app.logger.info(f"Error connecting to S3 bucket: {e}")


@app.route('/api/upload', methods=['POST'])
def upload_video():
    response={}

    try:
        
        title = request.form.get('title')
        description = request.form.get('description')
        thumbnailfile = request.files['thumbnail']
        videofile = request.files['video']
        
        response['text'] = f'title = {title}; description = {description}'
        response['file'] = f'video = {videofile.filename}; thumb = {thumbnailfile.filename}'

    except:

        response['text'] = f'Erro nos textos'
        response['file'] = f'Erro nos ficheiros'

        return jsonify(response)


    if not title or not thumbnailfile or not videofile:
        return jsonify({
                    "status": "error",
                    "message": f"Dados não fornecidos. Title: {title}, Description: {description}"
                }), 400

    try:
        s3_client.head_bucket(Bucket=AWS_S3_BUCKET)
    except Exception as e:
        response['s3']='nao conectado na s3'
        return jsonify(response)
    
    
    try:
        video_filename != None
        video_filename = videofile.filename
        temp_video_path = os.path.join("/tmp", video_filename)
        videofile.save(temp_video_path)
        duration = get_video_duration(temp_video_path)
        os.remove(temp_video_path)

        response['duration'] = 'carregado com duracao'

    except Exception as e:
        response['duration'] - 'nao conseguio duracao'

        app.logger.error(f"Erro ao obter duração do vídeo: {e}")
        return jsonify(response)




    try:
        thumbnailkey = thumbnailfile.filename

        #upload da thumbnail na s3 da AWS
        s3_client.upload_fileobj(thumbnailfile, AWS_S3_BUCKET, thumbnailkey)

        thumbnailurl = f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/{thumbnailkey}"

        response['s3thumb'] = 'thumb upload'
    except Exception as e:
        response['s3thumb'] = 'nao ocurrou upload da thumb'

        return jsonify(response)


    try:

        videokey = videofile.filename

        s3_client.upload_fileobj(videofile, AWS_S3_BUCKET, videokey)

        videourl = f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/{videokey}"

        response['s3video'] = 'video upload'
    except Exception as e:
        response['s3video'] = 'nao ocorreu o upload do video'
        return jsonify(response)
    


    try:
        videos_collection.insert_one({
        "title": title,
        "thumbnailurl": thumbnailurl,
        "videourl": videourl,
        "description": description,
        "duration": duration
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Erro ao adicionar os dados na DB'}, 500)

    app.logger.info(f"Upload acabado")
    
    return jsonify(response)


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