import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    MONGO_URI= "mongodb+srv://user:user@cluster0.u3fdtma.mongodb.net/statuspage?appName=Cluster0"
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")
