from pymongo import MongoClient
import boto3


# Conectar à MongoDB
client = MongoClient('mongodb://admin:password123@mongodb:27017/')
db = client.videos_db
videos_collection = db.videos

AWS_S3_BUCKET = 'ualflix'
s3_client = boto3.client('s3', region_name='eu-west-3')