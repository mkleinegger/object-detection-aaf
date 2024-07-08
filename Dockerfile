FROM python:3.9-slim

WORKDIR /app
COPY ./requirements.txt .

RUN pip install -r ./requirements.txt

COPY ./yolo_configs/ ./yolo_configs/
COPY ./src/app.py ./src/yolo_model.py /app/

ENTRYPOINT ["python", "/app/app.py"]