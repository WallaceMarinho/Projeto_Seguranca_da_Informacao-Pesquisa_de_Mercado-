from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from so_user_management import create_admin, list_users, remove_user_by_id, update_terms_policy, update_user
from db_connection import mydb

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/admin_dashboard')
def admin_dashboard():
    user_role = session.get('role')

    if user_role != 'admin':
        flash("Acesso negado.", "error")
        return redirect(url_for('app_routes.login'))

    users = list_users(mydb, 'user')  # Ajustado para usar a função list_users
    admins = list_users(mydb, 'admin')  # Agora usa a mesma função para admins
    is_default_admin = session.get('is_default_admin', False)

    admin_email = session.get('email')  # Ajuste conforme sua lógica de autenticação
    user = None
    if admin_email:
        with mydb.cursor() as cursor:
            cursor.execute("SELECT * FROM user_login WHERE email = %s", (admin_email,))
            user = cursor.fetchone() or {}  # Garante que será um dicionário vazio se não houver usuário

    return render_template('admin_dashboard.html', user=user, user_role=user_role, 
                           is_default_admin=is_default_admin, users=users, admins=admins)

# Rota para Atualizar Conta
@admin_routes.route('/update_account', methods=['POST'])
def update_account():
    form_data = request.form
    update_user(form_data['email'], mydb)
    flash("Conta atualizada com sucesso!")
    return redirect(url_for('admin_routes.admin_dashboard'))

# Rota para Atualizar Termos e Política
@admin_routes.route('/update_policy_terms', methods=['POST'])
def update_policy_terms():
    if 'role' in session and session['role'] == 'admin':
        form_data = request.form
        type = form_data.get('type')
        content = form_data.get('content')
        update_terms_policy(mydb, type, content)
        return redirect(url_for('admin_routes.admin_dashboard'))
    else:
        return redirect(url_for('app_routes.login', error_message="Acesso negado."))

@admin_routes.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form.get('user_id')  # Obtém o ID do usuário do formulário
    admin_email = session.get('email')
    user_role = session.get('role')

    if user_role != 'admin':  # Verifica se o usuário logado é um admin
        flash("Você não tem permissão para realizar esta ação.", "error")
        return redirect(url_for('admin_routes.admin_dashboard'))

    if user_role == 'admin':
        is_default_admin = session.get('is_default_admin', False)
        # Admin padrão pode remover qualquer um
        if is_default_admin or user_role == 'admin':
            if remove_user_by_id(user_id, admin_email, mydb):
                flash("Usuário removido com sucesso.", "success")
            else:
                flash("Erro ao remover o usuário.", "error")
        else:
            flash("Você não tem permissão para remover usuários admin.", "error")
    return redirect(url_for('admin_routes.admin_dashboard'))
