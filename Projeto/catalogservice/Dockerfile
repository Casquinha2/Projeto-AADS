FROM python

WORKDIR /app

COPY main.py .

RUN pip install flask flask-cors pymongo

EXPOSE 5000

CMD ["python","main.py"]