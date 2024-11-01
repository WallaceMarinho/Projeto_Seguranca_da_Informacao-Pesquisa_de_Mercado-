import bcrypt
from flask import jsonify, request
from pymysql.cursors import DictCursor

from so_terms_login import get_terms_and_privacy, log_event

def view_user_data(user_id, mydb):
    with mydb.cursor(cursor=DictCursor) as cursor:
        cursor.execute("USE surveydb")
        cursor.execute("SELECT nome, sobrenome, telefone, bairro, email, role, provider FROM user_login WHERE id = %s", (user_id,))
        row = cursor.fetchone()

        if row:
            return {
                'nome': row['nome'],
                'sobrenome': row['sobrenome'],
                'telefone': row['telefone'],
                'bairro': row['bairro'],
                'email': row['email'],
                'role': row['role'],
                'provider': row['provider']
            }
        return None

def edit_user_data(user_id, mydb):
    cursor = mydb.cursor()
    cursor.execute("USE surveydb")
    
    nome = request.form.get('nome', '').strip()
    sobrenome = request.form.get('sobrenome', '').strip()
    telefone = request.form.get('telefone', '').strip()
    senha = request.form.get('senha', '').strip()
    bairro = request.form.get('bairro', '').strip()

    if senha and (len(senha) != 6 or not senha.isdigit()):
        return jsonify({"success": False, "message": "A senha deve ter exatamente 6 dígitos."})

    if nome:
        cursor.execute("UPDATE user_login SET nome = %s WHERE id = %s", (nome, user_id))
    if sobrenome:
        cursor.execute("UPDATE user_login SET sobrenome = %s WHERE id = %s", (sobrenome, user_id))
    if telefone:
        cursor.execute("UPDATE user_login SET telefone = %s WHERE id = %s", (telefone, user_id))
    if senha:
        cursor.execute("UPDATE user_login SET password = %s WHERE id = %s", (senha, user_id))
    if bairro:
        cursor.execute("UPDATE user_login SET bairro = %s WHERE id = %s", (bairro, user_id))

    mydb.commit()
    return jsonify({"success": True, "message": "Dados pessoais atualizados com sucesso."})

def get_user_terms_status(user_id, mydb):
    try:
        cursor = mydb.cursor(DictCursor)
        cursor.execute("USE surveydb")

        cursor.execute("SELECT terms_version, privacy_version, optional_version FROM user_terms_and_privacy_acceptance WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            return {
                'terms_version': result['terms_version'],
                'privacy_version': result['privacy_version'],
                'optional': result['optional_version']
            }
        else:
            return {
                'error': True,
                'message': "O banco de dados está sem versões dos termos e política de privacidade."
            }
    except Exception as e:
        print(f"Erro ao buscar status dos termos: {e}")
        return {
            'error': True,
            'message': "Erro ao acessar o banco de dados."
        }

def update_user_optional_terms(user_id, optional_terms_accepted, mydb):
    try:
        cursor = mydb.cursor()
        cursor.execute("USE surveydb")

        terms_data = get_terms_and_privacy(mydb)
        optional_version = None

        if optional_terms_accepted:
            if terms_data:
                optional_version = terms_data['optional_version']
                cursor.execute("UPDATE user_terms_and_privacy_acceptance SET optional_version = %s, accepted_at = CURRENT_TIMESTAMP WHERE user_id = %s", 
                               (optional_version, user_id))
            else:
                return False

        else:
            cursor.execute("UPDATE user_terms_and_privacy_acceptance SET optional_version = NULL WHERE user_id = %s", 
                           (user_id,))

        mydb.commit()
        result = cursor.rowcount > 0
        if result:
            if optional_terms_accepted:
                log_event("Aceitação dos termos opcionais", "user_terms_and_privacy_acceptance", user_id, f"Versão aceita: {optional_version}")
            else:
                log_event("Rejeição dos termos opcionais", "user_terms_and_privacy_acceptance", user_id, "Versão agora: NULL")

        return result
    except Exception as e:
        print(f"Erro ao atualizar os termos opcionais: {e}")
        return False

def remove_local_user_account(user_id, password, mydb):
    with mydb.cursor(cursor=DictCursor) as cursor:
        cursor.execute("USE surveydb")
        cursor.execute("SELECT password FROM user_login WHERE id = %s", (user_id,))
        stored_password = cursor.fetchone()
        
        if stored_password and bcrypt.checkpw(password.encode('utf-8'), stored_password['password'].encode('utf-8')):
            cursor.execute("DELETE FROM user_login WHERE id = %s", (user_id,))
            mydb.commit()
            log_event("Conta de usuário removida", "user_login", user_id)
            return True
        return False

def remove_google_user_account(user_id, mydb):
    with mydb.cursor(cursor=DictCursor) as cursor:
        cursor.execute("USE surveydb")
        cursor.execute("DELETE FROM user_login WHERE id = %s", (user_id,))
        mydb.commit()
        log_event("Conta de usuário Google removida", "user_login", user_id)
        return True
