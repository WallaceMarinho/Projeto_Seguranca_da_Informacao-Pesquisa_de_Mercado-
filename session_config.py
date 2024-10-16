import os
from flask import Flask
from flask_session import Session
import redis

def configure_session(app: Flask):
    # Carregar variáveis de ambiente para evitar hardcoding de informações sensíveis
    app.config['SESSION_TYPE'] = 'redis'
    
    # Pegando a URL do Redis da variável de ambiente
    redis_url = os.getenv('REDIS_URL')
    app.config['SESSION_REDIS'] = redis.from_url(redis_url)
    
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    
    # Pegando a chave secreta da variável de ambiente
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
    # Inicializar a sessão
    Session(app)
