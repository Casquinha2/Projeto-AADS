import os

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

from pymongo import MongoClient
import boto3


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

try:
    AWS_S3_BUCKET = 'ualflix'
    s3_client = boto3.client('s3', region_name='eu-west-3')
    s3_client.head_bucket(Bucket=AWS_S3_BUCKET)
    app.logger.info("Connected to S3 bucket successfully!")
except Exception as e:
    app.logger.info(f"Error connecting to S3 bucket: {e}")


@app.route('/api/upload', methods=['POST'])
def upload_video():
    try:
        title = request.form.get('title')
        thumbnailfile = request.files.get('thumbnail')
        videofile = request.files.get('video')
        description = request.form.get('description')

        if not title or not thumbnailfile or not videofile:
            return jsonify({'status': 'error', 'message': 'Dados não fornecidos'}), 400
        
        video_filename = videofile.filename
        temp_video_path = os.path.join("/tmp", video_filename)
        
        # Save the uploaded video temporarily.
        videofile.save(temp_video_path)
        
        # Retrieve the duration.
        duration = get_video_duration(temp_video_path)

        os.remove(temp_video_path)

        thumbnailkey = thumbnailfile.filename

        #upload da thumbnail na s3 da AWS
        s3_client.upload_fileobj(
            thumbnailfile, AWS_S3_BUCKET, thumbnailkey,
            ExtraArgs={'ContentType': thumbnailfile.content_type, 'ACL': 'public_read'}
        )
        thumbnailurl = f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/{thumbnailkey}"

        videokey = videofile.filename

        s3_client.upload_fileobj(
            videofile, AWS_S3_BUCKET, videokey,
            ExtraArgs={'ContentType': videofile.content_type, 'ACL': 'public_read'}
        )
        videourl = f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/{videokey}"

        videos_collection.insert_one({
        "title": title,
        "thumbnailurl": thumbnailurl,
        "videourl": videourl,
        "description": description,
        "duration": duration
        })

        app.logger.info(f"Upload acabado")
        return jsonify({'status': 'success', 'message': 'Upload do video com sucesso'})
            
    except Exception as e:
        app.logger.error(f"Erro ao dar upload do video: {e}")
        return jsonify({'status': 'error', 'message': 'Erro interno do servidor'}), 500


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
    app.run(host='0.0.0.0', port=7000, debug=False)