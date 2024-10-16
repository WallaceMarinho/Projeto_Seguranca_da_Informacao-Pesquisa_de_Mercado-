from pymysql import IntegrityError
from db_connection import mydb

# Função para buscar os termos de uso da tabela no banco de dados
def get_terms_of_use(mydb):
    if mydb:
        with mydb.cursor() as cursor:
            cursor.execute("USE surveydb")
            cursor.execute("SELECT terms, optional_terms FROM terms_of_use ORDER BY version DESC LIMIT 1")
            terms = cursor.fetchone()
            
            if not terms:
                return {
                    "terms": "Você ainda não possui uma versão de termo obrigatório no banco de dados.",
                    "optional_terms": "Você ainda não possui uma versão de termo opcional no banco de dados."
                }

        return {
            "terms": terms['terms'],
            "optional_terms": terms['optional_terms'],
            "message": "Para cancelar o consentimento obrigatório, exclua sua conta ou solicite a exclusão em admin@system.com."
        }
    return None


bairros = [
		'EUGÊNIO DE MELO', 'JARDIM IPÊ', 'JARDIM ITAPUÃ', 
		'RESIDENCIAL ARMANDO MOREIRA RIGHI', 'RESIDENCIAL GALO BRANCO', 
		'CONJ. HAB. JARDIM SÃO JOSÉ', 'JARDIM AMERICANO', 'JARDIM COQUEIRO', 
		'JARDIM MOTORAMA', 'JARDIM NOVA DETROIT', 'JARDIM NOVA FLORIDA', 
		'JARDIM PARARANGABA', 'JARDIM RODOLFO', 'JARDIM SANTA INÊS I', 
		'JARDIM SANTA INÊS II', 'JARDIM SANTA INÊS III', 'JARDIM SÃO JOSÉ', 
		'JARDIM SÃO VICENTE', 'RESIDENCIAL ANA MARIA', 'RESIDENCIAL CAMPO BELO', 
		'RESIDENCIAL FREI GALVÃO', 'JARDIM CASTANHEIRA', 'JARDIM CEREJEIRAS', 
		'JARDIM NOVA MICHIGAN', 'JARDIM PAINEIRAS I', 'JARDIM PAINEIRAS II', 
		'JARDIM SAN RAFAEL', 'PARQUE NOVA ESPERANÇA', 'PARQUE NOVO HORIZONTE', 
		'RESIDENCIAL DOM BOSCO', 'CAMPOS DE SÃO JOSÉ', 'JARDIM HELENA', 
		'JARDIM MARIANA', 'JARDIM MARIANA II', 'POUSADA DO VALE', 
		'VILA MONTERREY'
]

# Função para registrar um novo usuário no banco de dados
def register_user(mydb, form_data, accept_optional):
    nome = form_data.get('nome')
    sobrenome = form_data.get('sobrenome')
    telefone = form_data.get('telefone')
    email = form_data.get('email')
    senha = form_data.get('senha')
    bairro = form_data.get('bairro')
    
    if mydb:
        try:
            with mydb.cursor() as cursor:
                cursor.execute("USE surveydb")
                sql_user = """
                INSERT INTO user_login (nome, sobrenome, telefone, email, password, bairro, terms_mandatory_accepted, terms_optional_accepted)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_user, (nome, sobrenome, telefone, email, senha, bairro, True, accept_optional or False))
                mydb.commit()
                user_id = cursor.lastrowid
                return user_id
        except IntegrityError as e:
            if e.args[0] == 1062:  # Código de erro para duplicata
                return None  # Retorna None se o e-mail já estiver cadastrado
            else:
                raise  # Re-lança a exceção para outros tipos de erro
    return None

# Função para login do usuário
def login_user(mydb, form_data):
    email = form_data.get('email')
    senha = form_data.get('password')
    
    if mydb:
        with mydb.cursor() as cursor:
            cursor.execute("USE surveydb")
            cursor.execute("SELECT id FROM user_login WHERE email = %s AND password = %s", (email, senha))
            user = cursor.fetchone()
        return user['id'] if user else None
    return None

# Função para verificar se o usuário é admin
def is_admin(user_id, mydb):
    if mydb:
        with mydb.cursor() as cursor:
            cursor.execute("USE surveydb")
            cursor.execute("SELECT role FROM user_login WHERE id = %s", (user_id))
            user = cursor.fetchone()
        return user and user['role'] == 'admin'
    return False
