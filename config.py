import os
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from flask import Blueprint, Flask

load_dotenv()

config = {
    'ssh': {
        'host': os.getenv('SSH_HOST'),
        'port': int(os.getenv('SSH_PORT')),
        'username': os.getenv('SSH_USERNAME'),
        #'password': os.getenv('SSH_PASSWORD'),
        'private_key': os.getenv('SSH_PRIVATE_KEY'),
        'remote_bind_address': (os.getenv('REMOTE_DB_HOST'), int(os.getenv('REMOTE_DB_PORT')))
    },
    'mysql': {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'port': None
    }
}

def parse_params(params_str):
    if params_str:
        return dict(item.split('=') for item in params_str.split(','))
    return {}

# Obter valores do ambiente
authorize_params = parse_params(os.getenv('AUTHORIZE_PARAMS'))
access_token_params = parse_params(os.getenv('ACCESS_TOKEN_PARAMS'))
refresh_token_url=parse_params(os.getenv('REFRESH_TOKEN_URL'))

app = Flask(__name__)
# Inicializar OAuth
oauth = OAuth(app)
google = oauth.register(
    name=os.getenv('OAUTH_NAME'),
    client_id=os.getenv('GOOG_CLIENT_ID'),
    client_secret=os.getenv('GOOG_CLIENT_KEY'),
    access_token_url=os.getenv('ACCESS_TOKEN_URL'),
    authorize_url=os.getenv('AUTHORIZE_URL'),
    authorize_params=authorize_params or {},
    access_token_params=access_token_params or {},
    refresh_token_url=refresh_token_url or {},
    jwks_uri=os.getenv('JWKS_URI'),
    redirect_uri=os.getenv('REDIRECT_URI'),
    client_kwargs={
        'scope': 'openid profile email',
        'token_endpoint_auth_method': 'client_secret_post'
    }
)
userinfo = os.getenv('USERINFO_URL')