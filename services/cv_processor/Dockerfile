# services/cv_processor/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY worker.py requirements.txt ./
RUN pip install -r requirements.txt
CMD ["python", "worker.py"]
