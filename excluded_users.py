import json
import os

EXCLUDED_USERS_FILE = "excluded_users.json"

def load_excluded_users():
    """
    Carrega a lista de usuários excluídos do arquivo.
    Retorna uma lista de dicionários com as informações dos usuários.
    """
    if os.path.exists(EXCLUDED_USERS_FILE):
        try:
            with open(EXCLUDED_USERS_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Erro ao carregar o arquivo JSON. Inicializando uma nova lista.")
            return []
    return []

def add_to_excluded_users(user_data):
    """
    Adiciona as informações de um usuário à lista de excluídos.
    user_data deve ser um dicionário contendo as chaves: 'id', 'email', e 'data'.
    """
    if not isinstance(user_data, dict) or not {"id", "email", "data"}.issubset(user_data.keys()):
        raise ValueError("O parâmetro 'user_data' deve ser um dicionário com as chaves 'id', 'email', e 'data'.")

    excluded_users = load_excluded_users()

    # Verifica se o usuário já existe na lista
    if any(user["id"] == user_data["id"] for user in excluded_users):
        print(f"Usuário com ID {user_data['id']} já está na lista de excluídos. Nenhuma ação realizada.")
        return  # Não adiciona o ID duplicado

    # Adiciona o usuário à lista
    excluded_users.append(user_data)

    # Atualiza o arquivo JSON
    with open(EXCLUDED_USERS_FILE, "w") as file:
        json.dump(excluded_users, file, indent=4)
    print(f"Usuário com ID {user_data['id']} adicionado à lista de excluídos.")