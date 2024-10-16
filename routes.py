from flask import Blueprint, flash, render_template_string, render_template, request, redirect, session, url_for, jsonify
from middlewares import admin_required, login_required, registration_required, terms_accepted_required
from so_survey import read_survey_responses, submit_survey, survey, update_survey_responses, questions, response_options
from so_terms_login import register_user, login_user, is_admin, get_terms_of_use, bairros
from db_connection import mydb
from so_user import confirm_account_removal, edit_user_data, get_user_terms_status, update_user_terms, view_user_data

app_routes = Blueprint('app_routes', __name__)

# Página inicial
@app_routes.route('/')
def index():
    return render_template('index.html')

# Rota para exibir os termos de uso
@app_routes.route('/terms', methods=['GET'])
def terms():
    terms = get_terms_of_use(mydb)  # Busca os termos de uso do banco de dados
    return render_template('terms.html', terms=terms)

@app_routes.route('/terms/mandatory')
def mandatory_terms():
    # Obtém os termos do banco de dados
    terms_data = get_terms_of_use(mydb)
    
    # Verifica se os termos obrigatórios foram recuperados
    mandatory_terms_text = terms_data.get('terms')
    
    # Retorna o HTML com o termo obrigatório e o botão fechar
    return render_template_string(f"""
        <h2>Termos Obrigatórios</h2>
        <p>{mandatory_terms_text}</p>
        <div style="text-align: center; margin-top: 20px;">
            <button onclick="window.close()">Fechar</button>
        </div>
    """)

@app_routes.route('/terms/optional')
def optional_terms():
    # Obtém os termos do banco de dados
    terms_data = get_terms_of_use(mydb)
    
    # Verifica se os termos opcionais foram recuperados
    optional_terms_text = terms_data.get('optional_terms')
    
    # Retorna o HTML com o termo opcional e o botão fechar
    return render_template_string(f"""
        <h2>Termos Opcionais</h2>
        <p>{optional_terms_text}</p>
        <div style="text-align: center; margin-top: 20px;">
            <button onclick="window.close()">Fechar</button>
        </div>
    """)

# Rota temporária do Novo Usuário
@app_routes.route('/new_user')
def new_user():
    session['registering'] = True  # Define que o usuário está em processo de registro
    return redirect(url_for('app_routes.terms'))  # Redireciona para os termos

# Rota do Termo de Uso
@app_routes.route('/submit_terms', methods=['POST'])
def submit_terms():
    data = request.get_json()
    
    mandatory_accepted = data.get('mandatoryTermsAccepted', False)
    optional_accepted = data.get('optionalTermsAccepted', False)

    if mandatory_accepted:
        # Armazena a aceitação dos termos na sessão
        session['terms_accepted'] = {
            'mandatory': True,
            'optional': optional_accepted
        }

        if 'registering' in session:
            return jsonify({"message": "Termos aceitos. Redirecionando para registro..."}), 200

        # Se o usuário já está logado, redireciona para o menu
        user_id = session.get('user_id')
        if user_id:
            return redirect(url_for('app_routes.user_menu_route', user_id=user_id))

    return jsonify({"error": "Você deve aceitar os termos obrigatórios."}), 400

# Rota do Registro de Novo Usuário
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
                session['registering'] = True  # Define que o usuário está se registrando
                #session.pop('terms_accepted', None)
                return redirect(url_for('app_routes.survey_route', user_id=user_id))
            else:
                flash("E-mail já cadastrado. <a href='/login'>Faça login</a> ou tente com um e-mail diferente.", "error")
                return redirect(url_for('app_routes.novo_usuario'))  # Permite que o usuário permaneça na página de registro
        else:
            flash("Você deve aceitar os termos obrigatórios.")
    
    return render_template('novo_usuario.html', bairros=list_bairros)

# Rota para login do usuário
@app_routes.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None  # Inicializa a variável para a mensagem de erro
    if request.method == 'POST':
        form_data = request.form
        user_id = login_user(mydb, form_data)
        if user_id:
            session['user_id'] = user_id
            # Limpa a flag 'registering' após o login bem-sucedido
            session.pop('registering', None)

            if is_admin(user_id, mydb):
                return redirect(url_for('app_routes.admin'))
            return redirect(url_for('app_routes.survey_route', user_id=user_id))
        else:
            error_message = "Credenciais inválidas."  # Define a mensagem de erro
    return render_template('login.html', error_message=error_message)  # Passa a mensagem para o template

# Rota para o questionário
@app_routes.route('/survey/<int:user_id>', methods=['GET', 'POST'])
@login_required
def survey_route(user_id):
    if request.method == 'POST':
        return submit_survey(user_id)
    return survey(user_id)

# Rota para o menu do usuário
@app_routes.route('/user_menu', methods=['GET'])
@login_required
def user_menu_route():
    user_id = session.get('user_id')  # Obter o ID do usuário da sessão
    if not user_id:
        return redirect(url_for('app_routes.login'))  # Redirecionar para login se não houver ID do usuário
    
    # Apenas renderiza a página de menu do usuário
    return render_template('user_menu.html', user_id=user_id)

@app_routes.route('/get_user_data', methods=['GET'])
@login_required
def get_user_data_route():
    user_id = request.args.get('user_id')
    list_bairros = sorted(bairros)
    
    # Supondo que 'mydb' seja o objeto de conexão com o banco de dados
    user_data = view_user_data(user_id, mydb)

    if user_data:
        return jsonify({
            'success': True,
            'user': {
                'nome': user_data['nome'],
                'sobrenome': user_data['sobrenome'],
                'telefone': user_data['telefone'],
                'bairro': user_data['bairro'],
                'email': user_data['email']  # Inclui o email no retorno
            },
            'bairros': list_bairros  # Retorna a lista de bairros para o frontend
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
        user_responses = read_survey_responses(user_id, mydb)  # Lê as respostas do usuário
        
        # Mapeia as respostas do usuário com base no índice das perguntas
        user_responses_dict = {idx + 1: response['answer'] for idx, response in enumerate(user_responses)}
        user_dict = {key: int(value) for key, value in user_responses_dict.items()}

        return jsonify({
            'success': True,
            'questions': questions,
            'response_options': response_options,
            'user_responses': user_dict  # Passa as respostas do usuário como dicionário
        })
    else:
        return jsonify({'success': False, 'message': 'Usuário não autenticado.'})

@app_routes.route('/edit_survey_responses', methods=['POST'])
@login_required
def submit_edit_survey_responses():
    user_id = session.get('user_id')
    if user_id:
        data = request.form
        # Atualiza as respostas no banco de dados
        update_survey_responses(user_id, mydb, data)
        return jsonify({'success': True, 'message': 'Respostas atualizadas com sucesso.'})
    else:
        return jsonify({'success': False, 'message': 'Usuário não autenticado.'})

@app_routes.route('/manage_terms', methods=['POST'])
@login_required
def manage_terms_route():
    user_id = request.json.get('user_id')  # Obtém o ID do usuário da requisição
    terms_status = get_user_terms_status(user_id, mydb)  # Recupera o status atual dos termos

    return jsonify({
        'success': True,
        'mandatory_terms': True,  # Os termos obrigatórios estão sempre aceitos
        'optional_terms': terms_status['optional']  # Status dos termos opcionais do usuário
    })

@app_routes.route('/save_terms', methods=['POST'])
@login_required
def save_terms_route():
    user_id = request.json.get('user_id')
    optional_terms_accepted = request.json.get('optionalTerms', False)  # Se o checkbox dos termos opcionais foi marcado
    
    success = update_user_terms(user_id, optional_terms_accepted, mydb)  # Atualiza o consentimento no banco
    if success:
        return jsonify({'success': True, 'message': 'Termos salvos com sucesso.'})
    else:
        return jsonify({'success': False, 'message': 'Erro ao salvar os termos.'})

@app_routes.route('/remove_account', methods=['POST'])
@login_required
def remove_account_route():
    user_id = session.get('user_id')
    password = request.json.get('password')  # Obtém a senha da requisição

    if user_id:
        if confirm_account_removal(user_id, password, mydb):
            session.pop('user_id', None)  # Remove o ID do usuário da sessão após excluir a conta
            return jsonify({"success": True, "message": "Conta removida com sucesso."})
        return jsonify({"success": False, "message": "Senha inválida. Falha ao remover a conta."}), 400
    return jsonify({"success": False, "message": "Usuário não autenticado."}), 401

# Rota para exibir página de agradecimento após o questionário
@app_routes.route('/thank_you/<int:user_id>')
@login_required
def thank_you(user_id):
    return render_template('regards.html', user_id=user_id)

@app_routes.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()  # Limpa todos os dados da sessão
    return redirect(url_for('app_routes.index'))  # Redireciona para a página inicial

# Rota de admin
@app_routes.route('/admin')
@admin_required
def admin():
    return "Admin Page"
