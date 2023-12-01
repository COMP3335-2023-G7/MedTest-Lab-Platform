FROM python:3.8-slim
WORKDIR /app
# Copy only the necessary backend files
COPY ./Backend /app/Backend
RUN pip install --no-cache-dir -r /app/Backend/requirements.txt
CMD ["python", "/app/Backend/app.py"]
ENV AES_SECRET_KEY B374A26A71490437AA024E4FADD5B497FDFF1A8EA6FF12F6FB65AF2720B59CCF
