FROM python:3.8-slim
WORKDIR /app
# Copy only the necessary backend files
COPY ./Backend /app/Backend
RUN pip install --no-cache-dir -r /app/Backend/requirements.txt
CMD ["python", "/app/Backend/app.py"]
