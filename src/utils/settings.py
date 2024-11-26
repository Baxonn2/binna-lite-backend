from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_ASSISTANT_KEY = os.getenv('OPENAI_ASSISTANT_KEY')

AUTH_SECRET_KEY = os.getenv('AUTH_SECRET_KEY')
AUTH_TOKEN_ALGORITHM = os.getenv('AUTH_TOKEN_ALGORITHM')

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
USE_MYSQL = MYSQL_HOST is not None
MYSQL_CONNECTION_URL = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"

ERROR_ON_NULL = {
    'OPENAI_API_KEY': OPENAI_API_KEY, 
    'OPENAI_ASSISTANT_KEY': OPENAI_ASSISTANT_KEY, 
    'AUTH_SECRET_KEY': AUTH_SECRET_KEY, 
    'AUTH_TOKEN_ALGORITHM': AUTH_TOKEN_ALGORITHM
}

has_error = False

for key, env_value in ERROR_ON_NULL.items():
    if env_value == None:
        print(key, 'env var not found')
        has_error = True

if has_error == True:

    exit(-1)