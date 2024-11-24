from flask import Blueprint, flash, render_template, request, redirect, session, url_for, jsonify
from middlewares import admin_required, login_required, registration_required, terms_accepted_required
from so_survey import read_survey_responses, submit_survey, survey, update_survey_responses, questions, response_options
from so_terms_login import get_optional_term_by_id, get_user_optional_version, log_event, register_user, login_user, get_terms_and_privacy, bairros, update_user_terms_acceptance, verify_terms_version
from db_connection import mydb
from so_user import edit_user_data, get_user_terms_status, remove_google_user_account, remove_local_user_account, reset_user_terms_by_ids, update_user_optional_terms, verify_optional_terms_update, view_user_data
from config import google, userinfo
from pymysql.cursors import DictCursor

from so_user_management import fetch_current_terms

app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def index():
    return render_template('index.html')

@app_routes.route('/login/google')
def google_login():
    redirect_uri = url_for('app_routes.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app_routes.route('/callback')
def google_callback():
    token = google.authorize_access_token()

    try:
        resp = google.get(userinfo)
        resp.raise_for_status()
        user_info = resp.json()
    except Exception as e:
        flash(f'Erro ao recuperar informações do usuário: {str(e)}', 'error')
        return redirect(url_for('app_routes.login'))

    if 'email' in user_info:
        session['email'] = user_info['email']
        session['name'] = user_info['name']

        with mydb.cursor() as cursor:
            cursor.execute("USE surveydb")
            cursor.execute("SELECT id FROM user_login WHERE email = %s", (user_info['email'],))
            user_id = cursor.fetchone()

        if user_id:
            # Usuário já existe, procede com o login
            session['user_id'] = user_id['id']
            session['provider'] = 'google'
            terms_status = verify_terms_version(mydb, user_id['id'])

            if not terms_status['terms_ok'] or not terms_status['privacy_ok']:
                return redirect(url_for('app_routes.new_terms_route', alert='updated_terms'))

            return redirect(url_for('app_routes.survey_route', user_id=user_id['id']))

        else:
            if session.get('registering', False):
                return render_template('google_callback.html', 
                                       email=user_info['email'], 
                                       nome=user_info['given_name'], 
                                       sobrenome=user_info['family_name'])
            else:
                flash('Credenciais inválidas, verifique email ou cadastre-se.', 'error')
                return redirect(url_for('app_routes.login'))

    else:
        flash('Erro ao fazer login com o Google. Tente novamente.', 'error')
        return redirect(url_for('app_routes.login'))

@app_routes.route('/register', methods=['GET', 'POST'])
# @registration_required
# @terms_accepted_required
def register():
    list_bairros = sorted(bairros)
    if request.method == 'POST':
        form_data = request.form
        user_type = form_data.get('user_type')
        email = form_data.get('email')
        nome = form_data.get('nome')
        sobrenome = form_data.get('sobrenome')
        telefone = form_data.get('telefone')
        bairro = form_data.get('bairro')
    
        if user_type == 'local':
            senha = form_data.get('senha')
            if not senha or len(senha) != 6:
                flash('A senha deve ter exatamente 6 dígitos.', 'error')
                return redirect(url_for('app_routes.register'))
            
            with mydb.cursor() as cursor:
                cursor.execute("USE surveydb")
                cursor.execute("SELECT id FROM user_login WHERE email = %s", (email,))
                user = cursor.fetchone()

            if user:
                flash('O email já está cadastrado. Tente usar outro email ou faça login.', 'error')
                return redirect(url_for('app_routes.login'))

        elif user_type == 'google':
            email_from_session = session.get('email')
            if not email_from_session or email_from_session != email:
                flash('Erro: O email fornecido não corresponde ao email autenticado pelo Google.', 'error')
                return redirect(url_for('app_routes.register'))

            senha = None

        if len(telefone) != 11 or not telefone.isdigit():
            flash('Insira o Telefone com DDD.', 'error')
            return redirect(url_for('app_routes.register'))
        
        provider = 'local' if user_type == 'local' else 'google'
        user_id = register_user(
            mydb, nome, sobrenome, telefone, email, senha, bairro, provider
        )

        if user_id:
            session['provider'] = provider
            return redirect(url_for('app_routes.survey_route'))
        else:
            flash('Erro ao cadastrar usuário. Tente novamente.', 'error')
            return redirect(url_for('app_routes.register'))

    user_type = request.args.get('user_type', 'local') 
    email = request.args.get('email', '')

    return render_template('new_user.html', bairros=list_bairros, 
                           user_type=user_type, 
                           email=email, 
                           nome=request.args.get('nome', ''), 
                           sobrenome=request.args.get('sobrenome', ''))

@app_routes.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None 

    if request.method == 'POST':
        form_data = request.form
        login_result = login_user(mydb, form_data)
        print(login_result)

        if login_result:
            user_id = login_result["user_id"]
            session['user_id'] = user_id
            session['provider'] = login_result.get('provider')
            session['role'] = login_result.get('role')
            session['is_default_admin'] = login_result.get('is_default_admin')

            print(f"Role armazenada na sessão: {session['role']}")  # Para depuração
            print(f"Is default admin armazenado na sessão: {session['is_default_admin']}")  # Para depuração

            user_role = session.get("role")
            print(user_role)
            is_default_admin = session.get("is_default_admin")
            print(is_default_admin)
            session.pop('registering', None)

            # Verificar aceitação dos termos apenas se o usuário não for admin
            if user_role == 'user':
                terms_status = verify_terms_version(mydb, user_id)
                if not terms_status['terms_ok'] or not terms_status['privacy_ok']:
                    return redirect(url_for('app_routes.new_terms_route', alert='updated_terms'))

            # Redirecionar o admin ao dashboard diretamente, sem verificação de termos
            if user_role == 'admin' and is_default_admin:
                return redirect(url_for('admin_routes.admin_dashboard'))

            # Redirecionar o usuário comum para a rota survey_route
            return redirect(url_for('app_routes.survey_route', user_id=user_id))

        error_message = "Credenciais inválidas, verifique email e senha ou cadastre-se."
    return render_template('login.html', error_message=error_message)

@app_routes.route('/accept-terms', methods=['POST'])
def upd_terms_route():
    user_id = session.get('user_id')
    terms_accepted = request.form.get('terms')
    privacy_accepted = request.form.get('privacy')

    if user_id and terms_accepted and privacy_accepted:
        versions = verify_terms_version(mydb, user_id)
        print(f"[upd_terms_route] Versões verificadas para o usuário {user_id} - Termos OK: {versions['terms_ok']}, Política OK: {versions['privacy_ok']}")

        update_user_terms_acceptance(mydb, user_id, versions['current_terms_version'], versions['current_privacy_version'])

        return redirect(url_for('app_routes.survey_route'))
    return redirect(url_for('app_routes.login'))

@app_routes.route('/check_optional_terms_update', methods=['GET'])
def check_optional_terms_update():
    """
    Verifica se os termos opcionais aceitos pelo usuário estão atualizados
    e realiza o reset se necessário.
    """
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': 'Usuário não logado.'}), 401

    try:
        # Verifica atualizações nos termos opcionais
        optional_terms_status = verify_optional_terms_update(mydb, user_id)

        # Verifica versão global única de optional_version
        terms_data = get_terms_and_privacy(mydb)
        if terms_data:
            current_optional_version = terms_data['optional_version']
            user_optional_version = get_user_optional_version(mydb)

            # Se a versão global for maior, reseta o optional_version
            if user_optional_version is not None and user_optional_version < current_optional_version:
                reset_user_terms_by_ids(user_id, [], mydb, reset_global_version=True)
                optional_terms_status['updated'] = True
                optional_terms_status['was_accepted'] = True

        print(f"Status final da atualização: {optional_terms_status}")
        return jsonify(optional_terms_status)
    except Exception as e:
        print(f"Erro na verificação de termos opcionais: {e}")
        return jsonify({'error': 'Erro ao verificar atualização de termos opcionais.'}), 500

@app_routes.route('/accept-optional-terms', methods=['POST'])
def accept_optional_terms():
    user_id = session.get('user_id')
    optional_version = get_terms_and_privacy(mydb)['optional_version']
    update_user_optional_terms(user_id, optional_version, mydb)
    log_event("Aceitação dos Termos Opcionais", "user_terms_and_privacy_acceptance", user_id)
    return jsonify({"success": True})

@app_routes.route('/new-terms', methods=['GET', 'POST'])
def new_terms_route():
    user_id = session.get('user_id')
    if request.method == 'POST':
        terms_accepted = request.form.get('terms')
        privacy_accepted = request.form.get('privacy')

        if user_id and terms_accepted and privacy_accepted:
            versions = verify_terms_version(mydb, user_id)

            update_user_terms_acceptance(mydb, user_id, versions['current_terms_version'], versions['current_privacy_version'])
            return redirect(url_for('app_routes.survey_route'))

        return redirect(url_for('app_routes.login'))

    terms_status = verify_terms_version(mydb, user_id)
    terms_data = get_terms_and_privacy(mydb)

    return render_template('upd_terms.html',
                           terms_version=terms_data['terms_version'],
                           privacy_version=terms_data['privacy_version'],
                           terms_ok=terms_status['terms_ok'],
                           privacy_ok=terms_status['privacy_ok'],
                           terms_message="É necessário aceitar novamente para usar o site.")

@app_routes.route('/terms', methods=['GET'])
def terms():
    terms_data = get_terms_and_privacy(mydb)
    optional_terms = fetch_current_terms()
    return render_template(
        'terms.html',
        terms_data=terms_data,
        optional_terms=optional_terms
    )

@app_routes.route('/terms/mandatory')
def mandatory_terms():
    terms_data = get_terms_and_privacy(mydb)
    mandatory_terms_text = terms_data.get('terms')
    mandatory_terms_version = terms_data.get('terms_version')
    
    return render_template('terms_popup.html', title="Termos Obrigatórios",
                           content=mandatory_terms_text, version=mandatory_terms_version)

@app_routes.route('/terms/optional')
def optional_terms():
    terms_data = get_terms_and_privacy(mydb)
    optional_terms_text = terms_data.get('optional')
    optional_terms_version = terms_data.get('optional_version')
    
    return render_template('terms_popup.html', title="Recebimento de emails",
                           content=optional_terms_text, version=optional_terms_version)

@app_routes.route('/terms/privacy')
def privacy_policy():
    terms_data = get_terms_and_privacy(mydb)
    privacy_policy_text = terms_data.get('privacy')
    privacy_policy_version = terms_data.get('privacy_version')
    
    return render_template('terms_popup.html', title="Política de Privacidade",
                           content=privacy_policy_text, version=privacy_policy_version)

@app_routes.route('/terms/optional/<int:optional_id>')
def optional_term(optional_id):
    print(f"Buscando termo opcional com ID: {optional_id}")
    
    term = get_optional_term_by_id(optional_id, mydb)
    if term:
        return render_template(
            'terms_popup.html', 
            title=term['optional_code'],
            content=term['content'],
            version=term['version']
        )
    else:
        return "Termo opcional não encontrado.", 404

@app_routes.route('/new_user')
def new_user():
    session['registering'] = True
    return redirect(url_for('app_routes.terms'))

@app_routes.route('/submit_terms', methods=['POST'])
def submit_terms():
    data = request.get_json()

    # Verifica se os termos obrigatórios foram aceitos
    mandatory_accepted = data.get('mandatoryTermsAccepted', False)

    if mandatory_accepted:
        terms_data = get_terms_and_privacy(mydb)
        optional_terms_data = fetch_current_terms()

        # Obter dados dos termos opcionais aceitos
        accepted_optional_terms = [
            {
                'id': term['id'],
                'optional_code': term['optional_code'],
                'version': term['version']
            }
            for term in optional_terms_data if str(term['id']) in data.get('optionalTermsAccepted', [])
        ]

        # Salvar dados no session
        session['terms_accepted'] = {
            'mandatory': True,
            'privacy': True,  # Aceitação implícita da política de privacidade
            'terms_version': terms_data['terms_version'],
            'privacy_version': terms_data['privacy_version'],
            'optional_version': terms_data['optional_version'],  # Apenas se existir
            'optional_terms': accepted_optional_terms
        }

        return jsonify({"message": "Termos aceitos. Redirecionando para registro..."}), 200

    return jsonify({"error": "Você deve aceitar os Termos Obrigatórios para prosseguir."}), 400

@app_routes.route('/survey', methods=['GET', 'POST'])
# @terms_accepted_required
# @registration_required
def survey_route():
    user_id = session.get('user_id')
    if not user_id:
        print("Erro: user_id não está na sessão.")
        return redirect(url_for('app_routes.login'))

    if request.method == 'POST':
        return submit_survey(user_id)
    return survey(user_id)

@app_routes.route('/user_menu', methods=['GET'])
# @login_required
def user_menu_route():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('app_routes.login'))
    
    with mydb.cursor(cursor=DictCursor) as cursor:
        cursor.execute("USE surveydb")
        cursor.execute("SELECT provider FROM user_login WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        is_google_user = row['provider'] == 'google' if row else False

    return render_template('user_menu.html', user_id=user_id, is_google_user=is_google_user)

@app_routes.route('/manage_terms', methods=['GET'])
def manage_terms_route():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': True, 'message': 'User ID é obrigatório.'}), 400

    terms_status = get_user_terms_status(user_id, mydb)
    if 'error' in terms_status:
        return jsonify({'error': True, 'message': terms_status['message']}), 500

    return jsonify({'success': True, **terms_status}), 200

@app_routes.route('/save_terms', methods=['POST'])
def save_terms_route():
    data = request.get_json()
    user_id = data.get('user_id')
    optional_terms_accepted = data.get('optional_terms_accepted', [])

    if not user_id:
        return jsonify({'error': True, 'message': 'User ID é obrigatório.'}), 400

    # Atualiza os termos no banco de dados
    changes_made = update_user_optional_terms(user_id, optional_terms_accepted, mydb)

    # Retorna a mensagem com base no resultado
    if changes_made:
        return jsonify({'success': True, 'message': 'Termos opcionais atualizados com sucesso.'}), 200
    else:
        return jsonify({'success': True, 'message': 'Nenhuma alteração solicitada.'}), 200

@app_routes.route('/get_user_data', methods=['GET'])
# @login_required
def get_user_data_route():
    user_id = request.args.get('user_id')
    list_bairros = sorted(bairros)

    user_data = view_user_data(user_id, mydb)

    if user_data:
        return jsonify({
            'success': True,
            'user': {
                'nome': user_data['nome'],
                'sobrenome': user_data['sobrenome'],
                'telefone': user_data['telefone'],
                'bairro': user_data['bairro'],
                'email': user_data['email']
            },
            'bairros': list_bairros
        })
    else:
        return jsonify({'success': False, 'message': 'Usuário não encontrado.'}), 404

@app_routes.route('/edit_user_data', methods=['POST'])
# @login_required
def edit_user_data_route():
    user_id = session.get('user_id')
    if user_id:
        return edit_user_data(user_id, mydb)
    return jsonify({"success": False, "message": "Usuário não encontrado."}), 404

@app_routes.route('/edit_survey_responses', methods=['GET'])
# @login_required
def edit_survey_responses_route():
    user_id = session.get('user_id')
    if user_id:
        user_responses = read_survey_responses(user_id, mydb)

        user_responses_dict = {idx + 1: response['answer'] for idx, response in enumerate(user_responses)}
        user_dict = {key: int(value) for key, value in user_responses_dict.items()}

        return jsonify({
            'success': True,
            'questions': questions,
            'response_options': response_options,
            'user_responses': user_dict
        })
    else:
        return jsonify({'success': False, 'message': 'Usuário não autenticado.'})

@app_routes.route('/edit_survey_responses', methods=['POST'])
# @login_required
def submit_edit_survey_responses():
    user_id = session.get('user_id')
    if user_id:
        data = request.form
        update_survey_responses(user_id, mydb, data)
        return jsonify({'success': True, 'message': 'Respostas atualizadas com sucesso.'})
    else:
        return jsonify({'success': False, 'message': 'Usuário não autenticado.'})

@app_routes.route('/remove_account', methods=['POST'])
# @login_required
def remove_account_route():
    user_id = session.get('user_id')
    provider = session.get('provider')
    print(provider)

    # Verificar se o usuário está logado
    if not user_id:
        return jsonify({"success": False, "message": "Usuário não autenticado"}), 403

    # Log para ver qual usuário está sendo removido
    if provider == 'google':
        print(f"Removendo conta do usuário Google com ID: {user_id}")
        success = remove_google_user_account(user_id, mydb)  # Implementar esta função para remover conta do Google
    else:
        password = request.json.get('password')
        print(f"Removendo conta do usuário local com ID: {user_id}")
        success = remove_local_user_account(user_id, password, mydb)  # Implementar esta função para remover conta local

    if success:
        # Limpar a sessão após a remoção da conta
        session.pop('user_id', None)
        session.pop('provider', None)
        print("Sessão limpa após remoção da conta.")
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Falha ao remover a conta"}), 400

@app_routes.route('/thank_you')
# @login_required
def thank_you():
    user_id = session.get('user_id')
    return render_template('regards.html', user_id=user_id)

@app_routes.route('/logout', methods=['POST'])
# @login_required
def logout():
    session.clear()
    return redirect(url_for('app_routes.index'))
