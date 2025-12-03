import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
USERS_DATABASE = 'data/users.json'
DOCUMENTS_FOLDER = 'data/user_documents'
DEBUG = True
PORT = 5000