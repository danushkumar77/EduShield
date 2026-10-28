import os

class Config:
    """Base configuration class for EduShield."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-edushield-12345'
    
    # Database settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE = os.path.join(BASE_DIR, 'edushield.db')
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb+srv://danushkumardk07_db_user:danushkumar%405995@cluster0.22gafw4.mongodb.net/?retryWrites=true&w=majority&appName=EduShield'
    MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME') or 'edushield'
    
    # Flask settings
    DEBUG = True
    TESTING = False
