import os

# API URL used by the frontend to contact the backend API
# Default points to localhost with port 5000; in docker-compose the
# frontend will get `API_URL` from environment which should be `http://backend:5000`.
API_URL = os.environ.get("API_URL", "http://127.0.0.1:5000")
