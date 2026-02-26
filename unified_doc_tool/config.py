import os
import secrets

class Config:
    # Use environment variable or generate a random key for the session
    # (Note: Random key invalidates sessions on restart, which is secure for this tool)
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    PROCESSED_FOLDER = os.path.join(BASE_DIR, 'processed')
    SHARED_ASSETS_FOLDER = os.path.join(BASE_DIR, 'shared_assets')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

    # Ensure directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    os.makedirs(SHARED_ASSETS_FOLDER, exist_ok=True)
