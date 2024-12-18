from flask import Blueprint, jsonify, render_template, redirect, url_for, request, session, flash
from restore_backup import remove_user_and_register
from so_user import view_user_data
from so_user_management import create_admin, fetch_current_policy_terms, fetch_current_terms, fetch_user_dashboard_data, insert_optional_term_in_db, list_users, log_adm_event, remove_optional_term, remove_user_by_id, update_optional_term_in_db, update_terms_policy, update_user, update_user_email_in_db, validate_admin_password
from db_connection import mydb

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/admin_dashboard')
def admin_dashboard():
    if not mydb:
        flash("Erro ao conectar ao banco de dados.", "error")
        return redirect(url_for('app_routes.login'))
    
    user_role = session.get('role')
    if user_role != 'admin':
        flash("Acesso negado.", "error")
        return redirect(url_for('app_routes.login'))

    user = fetch_user_dashboard_data(session['user_id'])
    if user:
        session.update({
            'user_id': user['id'],
            'email': user['email'],
            'role': user['role'],
            'is_default_admin': user['is_default_admin'],
            'provider': user['provider']
        })
    
    return render_template(
        'admin_dashboard.html',
        user_role=user['role'],
        is_default_admin=user['is_default_admin']
    )

# Rota para Atualizar Conta
@admin_routes.route('/update_account', methods=['POST'])
def update_account():
    adm_id = session.get("user_id")
    if not adm_id:
        return jsonify({"success": False, "message": "Usuário não encontrado."}), 401

    form_data = request.form
    password_confirmation = form_data.get('password_confirmation')

    if not password_confirmation:
        return jsonify({"success": False, "message": "Senha de confirmação necessária."}), 400

    if not validate_admin_password(adm_id, password_confirmation):
        return jsonify({"success": False, "message": "Senha incorreta."}), 400

    telefone = form_data.get('telefone', '')
    if not telefone.isdigit() or len(telefone) != 11:
        return jsonify({"success": False, "message": "O campo telefone deve conter 11 dígitos numéricos."}), 400

    success = update_user(adm_id, form_data)
    log_adm_event("Atualização de conta bem-sucedida" if success else "Erro ao atualizar conta", changed_data=form_data)
    
    if success:
        return jsonify({"success": True, "message": "Conta atualizada com sucesso!"}), 200
    else:
        return jsonify({"success": False, "message": "Erro ao atualizar a conta."}), 500

@admin_routes.route('/get_policy_terms', methods=['GET'])
def get_policy_terms():
    if 'role' in session and session['role'] == 'admin':
        tipo = request.args.get('type')
        content = fetch_current_policy_terms(mydb, tipo)
        if content.get('success'):
            return jsonify(content)
        else:
            return jsonify(success=False, message="Termo não encontrado."), 404
    else:
        return jsonify(success=False, message="Acesso negado."), 403

@admin_routes.route('/update_policy_terms', methods=['POST'])
def update_policy_terms():
    if 'role' in session and session['role'] == 'admin':
        form_data = request.json
        if not form_data:
            return jsonify(success=False, message="Dados inválidos."), 400

        type = form_data.get('type')
        content = form_data.get('content')
        password = form_data.get('password')
        admin_id = session.get('user_id')

        if not password:
            return jsonify(success=False, message="Digite uma senha."), 400

        if validate_admin_password(admin_id, password):
            try:
                update_terms_policy(mydb, type, content)
                return jsonify(success=True, message="Termo ou política atualizados com sucesso!")
            except ValueError as ve:
                return jsonify(success=False, message=str(ve)), 400
            except Exception as e:
                return jsonify(success=False, message="Erro ao atualizar os termos ou políticas. Tente novamente mais tarde."), 500
        else:
            return jsonify(success=False, message="Senha incorreta."), 403
    else:
        return jsonify(success=False, message="Acesso negado."), 403

@admin_routes.route('/get_optional_terms', methods=['GET'])
def get_optional_terms():
    terms = fetch_current_terms()
    return jsonify({"optional_terms": terms, "success": True})

@admin_routes.route('/create_optional_term', methods=['POST'])
def create_optional_term():
    data = request.json
    content = data.get('content')

    if not content:
        return jsonify({"message": "O conteúdo do termo não pode estar vazio.", "success": False}), 400

    try:
        insert_optional_term_in_db(content)
        return jsonify({"message": "Novo termo opcional inserido com sucesso.", "success": True})
    except Exception as e:
        return jsonify({"message": f"Erro ao inserir o termo: {str(e)}", "success": False}), 500

@admin_routes.route('/update_optional_term/<int:term_id>', methods=['PUT'])
def update_optional_term(term_id):
    data = request.json
    new_content = data.get('content')

    if not new_content:
        return jsonify({"message": "O conteúdo do termo não pode estar vazio.", "success": False}), 400

    try:
        update_optional_term_in_db(term_id, new_content)
        return jsonify({"message": "Termo opcional atualizado com sucesso.", "success": True})
    except Exception as e:
        return jsonify({"message": f"Erro ao atualizar o termo: {str(e)}", "success": False}), 500

@admin_routes.route('/delete_optional_term/<int:term_id>', methods=['DELETE'])
def delete_optional_term(term_id):
    remove_optional_term(term_id)
    return jsonify({"message": "Termo opcional excluído com sucesso.", "success": True})

@admin_routes.route('/get_users', methods=['GET'])
def get_users():
    user_role = session.get('role')
    if user_role == 'admin':
        users = list_users(mydb, 'user')
        return jsonify({'users': users})
    else:
        return jsonify({'error': 'Acesso não autorizado'}), 403

@admin_routes.route('/update_user_email', methods=['POST'])
def update_user_email():
    user_id = request.form.get('user_id')
    new_email = request.form.get('email')
    senha_confirm = request.form.get('senha_confirm')
    adm_id = session.get('user_id')

    if not senha_confirm:
        flash("Campo de senha não pode estar vazio. Por favor, tente novamente.", "error")
        return redirect(url_for('admin_routes.admin_dashboard'))

    if not validate_admin_password(adm_id, senha_confirm):
        flash("Senha incorreta. Atualização não realizada.", "error")
        return redirect(url_for('admin_routes.admin_dashboard'))

    try:
        update_user_email_in_db(user_id, new_email)
        flash("E-mail atualizado com sucesso.", "success")
    except Exception as e:
        flash(str(e), "error")

    return redirect(url_for('admin_routes.admin_dashboard'))

@admin_routes.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form.get('user_id')
    senha_confirm = request.form.get('senha_confirm')
    user_role = session.get('role')
    adm_id = session.get('user_id')

    if user_role != 'admin':
        flash("Você não tem permissão para realizar esta ação.", "error")
        return redirect(url_for('admin_routes.admin_dashboard'))

    if not senha_confirm:
        flash("Senha não fornecida. Por favor, tente novamente.", "error")
        return redirect(url_for('admin_routes.admin_dashboard'))

    if not validate_admin_password(adm_id, senha_confirm):
        flash("Senha incorreta. Não foi possível remover o usuário.", "error")
        return redirect(url_for('admin_routes.admin_dashboard'))

    # Utilizando a nova função para remover e registrar a exclusão
    success = remove_user_and_register(user_id, mydb, log_exclusion=True)

    if success:
        flash("Usuário removido com sucesso.", "success")
    else:
        flash("Erro ao remover o usuário.", "error")

    return redirect(url_for('admin_routes.admin_dashboard'))

@admin_routes.route('/get_admins', methods=['GET'])
def get_admins():
    user_role = session.get('role')
    is_default_admin = session.get('is_default_admin')

    if user_role == 'admin' and is_default_admin:
        admins = list_users(mydb, 'admin')
        return jsonify({'admins': admins})
    else:
        return jsonify({'error': 'Acesso não autorizado'}), 403

@admin_routes.route('/logout', methods=['POST'])
# @login_required
def logout():
    session.clear()
    return redirect(url_for('app_routes.index'))