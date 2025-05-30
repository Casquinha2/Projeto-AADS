FROM python

WORKDIR /app

COPY main.py .

RUN pip install flask flask-cors pymongo moviepy boto3

EXPOSE 7000

CMD ["python","main.py"]
