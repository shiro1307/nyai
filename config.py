import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
DATABASE_NAME = 'legal_assistant.json'
DEBUG = True
PORT = 5000