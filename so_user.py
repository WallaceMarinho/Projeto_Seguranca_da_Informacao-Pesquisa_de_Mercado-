from flask import jsonify, request
from pymysql.cursors import DictCursor
from werkzeug.security import check_password_hash

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

def update_user_optional_terms(user_id, accepted, mydb):
    try:
        cursor = mydb.cursor()
        cursor.execute("USE surveydb")
        cursor.execute("UPDATE user_terms_and_privacy_acceptance SET optional_version = %s WHERE user_id = %s", 
                       (accepted, user_id))
        mydb.commit()
        result = cursor.rowcount > 0
        if result:
            terms_info = get_terms_and_privacy(mydb)
            if terms_info:
                version_info = f"Versão dos Termos Opcionais: {terms_info['optional_version']}"
                log_event("Alteração nos termos opcionais", "user_terms_and_privacy_acceptance", user_id, additional_info=version_info)

        return result
    except Exception as e:
        print(f"Erro ao atualizar os termos opcionais: {e}")
        return False

def confirm_account_removal(user_id, password, is_google_user, mydb):
    with mydb.cursor(cursor=DictCursor) as cursor:
        cursor.execute("USE surveydb")

        if is_google_user:
            cursor.execute("DELETE FROM user_login WHERE id = %s", (user_id,))
            mydb.commit()
            return {"success": True, "message": "Conta excluída com sucesso."}

        cursor.execute("SELECT password FROM user_login WHERE id = %s", (user_id,))
        stored_password = cursor.fetchone()

        if stored_password and check_password_hash(stored_password['password'], password):
            cursor.execute("DELETE FROM user_login WHERE id = %s", (user_id,))
            mydb.commit()

            log_event("Conta de usuário removida", "user_login", user_id)
            return {"success": True, "message": "Conta excluída com sucesso."}
        else:
            return {"success": False, "message": "Senha incorreta."}
