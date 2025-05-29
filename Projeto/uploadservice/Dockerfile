FROM python

WORKDIR /app

COPY uploadservice/main.py .

COPY uploadservice/requirements.txt .

COPY shared/ ./shared/

RUN pip install -r requirements.txt

EXPOSE 7000

CMD ["python","app.py"]