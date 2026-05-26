# services/api/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY cv_handler.py requirements_api.txt ./
RUN pip install -r requirements_api.txt
CMD ["python", "cv_handler.py"]
