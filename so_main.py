import os
import signal
from flask import Flask, request, jsonify
from routes import app_routes
from session_config import configure_session
from so_create_adm import create_default_admin
from db_connection import mydb, tunnel, keep_connection_alive
from so_create_db import create_tables

app = Flask(__name__)

configure_session(app)

def init_app():
    if mydb:
        try:
            create_tables(mydb)
            create_default_admin(mydb)
        except Exception as e:
            print(f"Erro ao executar a inicialização: {e}")
    else:
        raise ConnectionError("Erro ao conectar ao banco de dados.")

def close_connection():
    global tunnel, mydb
    if mydb:
        try:
            mydb.close()
            print("Conexão com o banco de dados fechada.")
        except Exception as e:
            print(f"Erro ao fechar a conexão com o banco de dados: {e}")
    if tunnel:
        try:
            if tunnel.is_active:
                tunnel.close()
                print("Túnel SSH fechado.")
        except Exception as e:
            print(f"Erro ao fechar o túnel SSH: {e}")

# Função para lidar com SIGINT (CTRL+C)
def handle_sigint(signal, frame):
    print("CTRL+C capturado! Encerrando a aplicação...")
    close_connection()
    exit(0)

# Certifique-se de que o código de inicialização só seja executado uma vez
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    signal.signal(signal.SIGINT, handle_sigint)

    try:
        init_app()  # Executa a inicialização da aplicação

        # Inicia a função para manter a conexão ativa
        import threading
        threading.Thread(target=keep_connection_alive, daemon=True).start()

    except ConnectionError as e:
        print(e)
        exit(1)

app.register_blueprint(app_routes)

# Rota para encerrar a aplicação com código de segurança
@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_code = request.json.get('shutdown_code')
    correct_code = os.getenv('SHUTDOWN_CODE')

    if shutdown_code == correct_code:
        close_connection()
        shutdown_func = request.environ.get('werkzeug.server.shutdown')
        if shutdown_func is None:
            raise RuntimeError('Não foi possível encerrar o servidor.')
        shutdown_func()
        return jsonify({"message": "Servidor encerrado com sucesso."}), 200
    else:
        return jsonify({"message": "Código de shutdown incorreto."}), 403

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)


# ------------------------------------------------------------
# from so_create_adm import create_default_admin
# from so_terms_login import main
# from so_create_db import connect, create_tables 

# if __name__ == "__main__":
#     tunnel, mydb = connect()

#     if mydb:
#         try:
#             create_tables(mydb)					# Cria as Tabelas
#             create_default_admin(mydb)  # Passa a conexão para a função
#             main(tunnel, mydb)					# Passa a conexão para o main também
#         finally:
#             mydb.close()
#             tunnel.close()
#     else:
#         print("Erro ao conectar ao banco de dados.")

# ------------------------------------------------------------

# from flask import Flask, request, jsonify, render_template
# from so_create_adm import create_default_admin
# from so_terms_login import main
# from so_create_db import connect, create_tables

# app = Flask(__name__, template_folder='.')

# # Página principal com HTML
# @app.route('/')
# def index():
#     return render_template('/index.html')  # Carrega o arquivo HTML

# # Endpoint para inicializar o banco de dados
# @app.route('/initialize_db', methods=['POST'])
# def initialize_db():
#     tunnel, mydb = connect()
#     if mydb:
#         try:
#             create_tables(mydb)   # Cria as Tabelas
#             create_default_admin(mydb)  # Cria admin
#             return jsonify({"message": "Database and admin initialized successfully!"})
#         finally:
#             mydb.close()
#             tunnel.close()
#     else:
#         return jsonify({"error": "Error connecting to the database."}), 500

# # Endpoint para rodar a aplicação principal
# @app.route('/run', methods=['POST'])
# def run_app():
#     tunnel, mydb = connect()
#     if mydb:
#         try:
#             main(tunnel, mydb)   # Passa a conexão para o main também
#             return jsonify({"message": "Application ran successfully!"})
#         finally:
#             mydb.close()
#             tunnel.close()
#     else:
#         return jsonify({"error": "Error connecting to the database."}), 500

# if __name__ == "__main__":
#     app.run(debug=True)

