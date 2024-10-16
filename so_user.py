from flask import jsonify, request
from pymysql.cursors import DictCursor

def view_user_data(user_id, mydb):
    with mydb.cursor(cursor=DictCursor) as cursor:
        cursor.execute("USE surveydb")
        cursor.execute("SELECT nome, sobrenome, telefone, bairro, email FROM user_login WHERE id = %s", (user_id,))
        row = cursor.fetchone()

        if row:
            return {
                'nome': row['nome'],
                'sobrenome': row['sobrenome'],
                'telefone': row['telefone'],
                'bairro': row['bairro'],
                'email': row['email'] 
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
    cursor = mydb.cursor(DictCursor)
    cursor.execute("USE surveydb")
    
    cursor.execute("SELECT terms_optional_accepted FROM user_login WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    
    if result:
        return {'optional': result['terms_optional_accepted']}
    else:
        return {'optional': False}

def update_user_terms(user_id, optional_terms_accepted, mydb):
    cursor = mydb.cursor()
    cursor.execute("USE surveydb")
    
    cursor.execute("UPDATE user_login SET terms_optional_accepted = %s WHERE id = %s", (optional_terms_accepted, user_id))
    mydb.commit()

    return cursor.rowcount > 0

def confirm_account_removal(user_id, password, mydb):
    cursor = mydb.cursor()
    cursor.execute("USE surveydb")

    cursor.execute("SELECT password FROM user_login WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    
    if result and password == result['password']:
        cursor.execute("DELETE FROM user_login WHERE id = %s", (user_id,))
        mydb.commit()
        return True
    else:
        return False
