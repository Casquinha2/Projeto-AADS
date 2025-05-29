FROM python

WORKDIR /app

COPY streamingservice/main.py .

COPY streamingservice/requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 6000

CMD ["python","app.py"]