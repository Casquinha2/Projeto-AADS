FROM python:3.8-slim

WORKDIR /app

COPY main.py .

RUN pip install flask flask-cors pymongo

EXPOSE 8080

CMD ["python","main.py"]