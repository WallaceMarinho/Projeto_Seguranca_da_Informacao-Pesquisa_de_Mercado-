from flask import Blueprint, flash, render_template_string, render_template, request, redirect, session, url_for, jsonify
from middlewares import admin_required, login_required, registration_required, terms_accepted_required
from so_survey import read_survey_responses, submit_survey, survey, update_survey_responses, questions, response_options
from so_terms_login import register_user, login_user, is_admin, get_terms_of_use, bairros
from db_connection import mydb
from so_user import confirm_account_removal, edit_user_data, get_user_terms_status, update_user_terms, view_user_data

app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def index():
    return render_template('index.html')

@app_routes.route('/terms', methods=['GET'])
def terms():
    terms = get_terms_of_use(mydb)
    return render_template('terms.html', terms=terms)

@app_routes.route('/terms/mandatory')
def mandatory_terms():
    terms_data = get_terms_of_use(mydb)
    mandatory_terms_text = terms_data.get('terms')
    
    return render_template_string(f"""
        <h2>Termos Obrigatórios</h2>
        <p>{mandatory_terms_text}</p>
        <div style="text-align: center; margin-top: 20px;">
            <button onclick="window.close()">Fechar</button>
        </div>
    """)

@app_routes.route('/terms/optional')
def optional_terms():
    terms_data = get_terms_of_use(mydb)
    optional_terms_text = terms_data.get('optional_terms')
    
    return render_template_string(f"""
        <h2>Termos Opcionais</h2>
        <p>{optional_terms_text}</p>
        <div style="text-align: center; margin-top: 20px;">
            <button onclick="window.close()">Fechar</button>
        </div>
    """)

@app_routes.route('/new_user')
def new_user():
    session['registering'] = True
    return redirect(url_for('app_routes.terms'))

@app_routes.route('/submit_terms', methods=['POST'])
def submit_terms():
    data = request.get_json()
    
    mandatory_accepted = data.get('mandatoryTermsAccepted', False)
    optional_accepted = data.get('optionalTermsAccepted', False)

    if mandatory_accepted:
        session['terms_accepted'] = {
            'mandatory': True,
            'optional': optional_accepted
        }

        if 'registering' in session:
            return jsonify({"message": "Termos aceitos. Redirecionando para registro..."}), 200

        user_id = session.get('user_id')
        if user_id:
            return redirect(url_for('app_routes.user_menu_route', user_id=user_id))

    return jsonify({"error": "Você deve aceitar os termos obrigatórios."}), 400

@app_routes.route('/register', methods=['GET', 'POST'])
@registration_required
@terms_accepted_required
def novo_usuario():
    list_bairros = sorted(bairros)

    if request.method == 'POST':
        form_data = request.form
        mandatory_accepted = session.get('terms_accepted', {}).get('mandatory', False)
        
        if mandatory_accepted:
            user_id = register_user(mydb, form_data, session.get('terms_accepted', {}).get('optional', False))
            if user_id:
                session['registering'] = True
                #session.pop('terms_accepted', None)
                return redirect(url_for('app_routes.survey_route', user_id=user_id))
            else:
                flash("E-mail já cadastrado. <a href='/login'>Faça login</a> ou tente com um e-mail diferente.", "error")
                return redirect(url_for('app_routes.novo_usuario'))
        else:
            flash("Você deve aceitar os termos obrigatórios.")
    
    return render_template('novo_usuario.html', bairros=list_bairros)

@app_routes.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None 
    if request.method == 'POST':
        form_data = request.form
        user_id = login_user(mydb, form_data)
        if user_id:
            session['user_id'] = user_id
            session.pop('registering', None)

            if is_admin(user_id, mydb):
                return redirect(url_for('app_routes.admin'))
            return redirect(url_for('app_routes.survey_route', user_id=user_id))
        else:
            error_message = "Credenciais inválidas."
    return render_template('login.html', error_message=error_message)

@app_routes.route('/survey/<int:user_id>', methods=['GET', 'POST'])
@login_required
def survey_route(user_id):
    if request.method == 'POST':
        return submit_survey(user_id)
    return survey(user_id)

@app_routes.route('/user_menu', methods=['GET'])
@login_required
def user_menu_route():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('app_routes.login'))
    
    return render_template('user_menu.html', user_id=user_id)

@app_routes.route('/get_user_data', methods=['GET'])
@login_required
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
@login_required
def edit_user_data_route():
    user_id = session.get('user_id')
    if user_id:
        return edit_user_data(user_id, mydb)
    return jsonify({"success": False, "message": "Usuário não encontrado."}), 404

@app_routes.route('/edit_survey_responses', methods=['GET'])
@login_required
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
@login_required
def submit_edit_survey_responses():
    user_id = session.get('user_id')
    if user_id:
        data = request.form
        update_survey_responses(user_id, mydb, data)
        return jsonify({'success': True, 'message': 'Respostas atualizadas com sucesso.'})
    else:
        return jsonify({'success': False, 'message': 'Usuário não autenticado.'})

@app_routes.route('/manage_terms', methods=['POST'])
@login_required
def manage_terms_route():
    user_id = request.json.get('user_id')
    terms_status = get_user_terms_status(user_id, mydb)

    return jsonify({
        'success': True,
        'mandatory_terms': True,
        'optional_terms': terms_status['optional']
    })

@app_routes.route('/save_terms', methods=['POST'])
@login_required
def save_terms_route():
    user_id = request.json.get('user_id')
    optional_terms_accepted = request.json.get('optionalTerms', False)
    
    success = update_user_terms(user_id, optional_terms_accepted, mydb)
    if success:
        return jsonify({'success': True, 'message': 'Termos salvos com sucesso.'})
    else:
        return jsonify({'success': False, 'message': 'Erro ao salvar os termos.'})

@app_routes.route('/remove_account', methods=['POST'])
@login_required
def remove_account_route():
    user_id = session.get('user_id')
    password = request.json.get('password')

    if user_id:
        if confirm_account_removal(user_id, password, mydb):
            session.pop('user_id', None)
            return jsonify({"success": True, "message": "Conta removida com sucesso."})
        return jsonify({"success": False, "message": "Senha inválida. Falha ao remover a conta."}), 400
    return jsonify({"success": False, "message": "Usuário não autenticado."}), 401

@app_routes.route('/thank_you/<int:user_id>')
@login_required
def thank_you(user_id):
    return render_template('regards.html', user_id=user_id)

@app_routes.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('app_routes.index'))

@app_routes.route('/admin')
@admin_required
def admin():
    return "Admin Page"
