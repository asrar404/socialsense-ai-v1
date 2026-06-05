import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///socialsense.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 86400 * 30

    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')
    REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID', '')
    REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET', '')
    REDDIT_USER_AGENT = os.environ.get('REDDIT_USER_AGENT', 'SocialSenseAI/1.0')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    MAX_CONCURRENT_JOBS = int(os.environ.get('MAX_CONCURRENT_JOBS', '4'))
    MAX_JOBS_PER_USER = int(os.environ.get('MAX_JOBS_PER_USER', '20'))
    MAX_JOB_RUNTIME = int(os.environ.get('MAX_JOB_RUNTIME', '600'))
    JOB_HISTORY_RETENTION_DAYS = int(os.environ.get('JOB_HISTORY_RETENTION_DAYS', '30'))
    MAX_JOB_RETRIES = int(os.environ.get('MAX_JOB_RETRIES', '3'))

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'reports')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
