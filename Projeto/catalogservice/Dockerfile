FROM python

WORKDIR /app

COPY catalogservice/main.py .

COPY catalogservice/requirements.txt .

COPY shared/ ./shared/

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python","app.py"]