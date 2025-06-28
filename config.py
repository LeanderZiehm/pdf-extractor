import os

# Folder paths
UPLOAD_FOLDER = 'pdfs/'
EXTRACTED_FOLDER = 'extracted/'
ALLOWED_EXTENSIONS = {'pdf'}

# Secret key for session management
SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_here')
