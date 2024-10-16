import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'ssh': {
        'host': os.getenv('SSH_HOST'),
        'port': int(os.getenv('SSH_PORT')),
        'username': os.getenv('SSH_USERNAME'),
        'password': os.getenv('SSH_PASSWORD'),
        #'private_key': os.getenv('SSH_PRIVATE_KEY'),
        'remote_bind_address': (os.getenv('REMOTE_DB_HOST'), int(os.getenv('REMOTE_DB_PORT')))
    },
    'mysql': {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'port': None
    }
}
