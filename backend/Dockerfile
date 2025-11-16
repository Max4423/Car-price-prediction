FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/. .
# Ensure models directory is copied to backend/models/ in the image
COPY backend/models/ backend/models/

EXPOSE 5000

CMD ["python", "app.py"]
