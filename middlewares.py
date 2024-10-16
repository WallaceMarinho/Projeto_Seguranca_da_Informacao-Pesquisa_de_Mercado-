from flask import redirect, session, url_for, jsonify

# Middleware para verificar se o usuário está autenticado
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('app_routes.index'))
        return f(*args, **kwargs)
    return decorated_function

# Middleware para verificar se o usuário já aceitou os termos obrigatórios
def terms_accepted_required(f):
    def decorated_function(*args, **kwargs):
        terms_accepted = session.get('terms_accepted', {}).get('mandatory', False)
        if not terms_accepted:
            return redirect(url_for('app_routes.index'))
        return f(*args, **kwargs)
    return decorated_function

# Middleware para verificar se o usuário está registrado
def registration_required(f):
    def decorated_function(*args, **kwargs):
        if 'registering' not in session:
            return redirect(url_for('app_routes.index'))
        return f(*args, **kwargs)
    return decorated_function

# Middleware para verificar se o usuário está autenticado e é admin
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin', False):
            return redirect(url_for('app_routes.index'))
        return f(*args, **kwargs)
    return decorated_function
