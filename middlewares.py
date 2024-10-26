from flask import redirect, session, url_for
from functools import wraps

# Middleware para verificar se o usuário está autenticado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('app_routes.login'))
        return f(*args, **kwargs)
    return decorated_function

# Middleware para verificar se o usuário está autenticado com Google
def google_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session and 'email' not in session:
            return redirect(url_for('app_routes.login'))
        return f(*args, **kwargs)
    return decorated_function

# Middleware para verificar se o usuário está autenticado de qualquer forma
def any_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session and 'email' not in session:
            return redirect(url_for('app_routes.login'))
        return f(*args, **kwargs)
    return decorated_function

# Middleware para verificar se o usuário já aceitou os termos obrigatórios
def terms_accepted_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        terms_accepted = session.get('terms_accepted', {})
        mandatory_accepted = terms_accepted.get('mandatory', False)
        privacy_accepted = terms_accepted.get('privacy', False)

        if not mandatory_accepted or not privacy_accepted:
            return redirect(url_for('app_routes.index'))
        return f(*args, **kwargs)
    return decorated_function

# Middleware para verificar se o usuário está registrado
def registration_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'registering' not in session:
            return redirect(url_for('app_routes.index'))
        return f(*args, **kwargs)
    return decorated_function

# Middleware para verificar se o usuário está autenticado e é admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin', False):
            return redirect(url_for('app_routes.index'))
        return f(*args, **kwargs)
    return decorated_function
