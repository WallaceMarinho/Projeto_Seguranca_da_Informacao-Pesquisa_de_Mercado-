from so_create_db import connect
from so_survey import create_survey_response
from so_user import user_menu
from so_user_management import main as admin_main

def display_terms_of_use():
    print("\n----- Termos de Uso (Obrigatórios) -----")
    print("""\
    1. Coleta e Tratamento de Dados Pessoais
    Ao utilizar este sistema, você consente com a coleta e o tratamento de seus dados pessoais, 
    tais como nome, sobrenome, telefone, email, bairro e respostas às pesquisas, com a finalidade 
    de melhorar nossos serviços e personalizar sua experiência. Seus dados serão armazenados de 
    forma segura, conforme as exigências da Lei Geral de Proteção de Dados (LGPD).

    2. Finalidade dos Dados Coletados
    Seus dados serão utilizados exclusivamente para as finalidades descritas, incluindo a 
    identificação do usuário para acesso ao sistema e a análise de respostas coletadas para fins 
    estatísticos e de melhoria de nossos serviços.

    3. Compartilhamento de Dados
    Seus dados pessoais não serão compartilhados com terceiros sem o seu consentimento, exceto 
    quando necessário para o cumprimento de obrigações legais ou regulatórias.

    4. Direitos do Titular dos Dados
    Você tem o direito de acessar, corrigir, excluir ou limitar o tratamento de seus dados pessoais, 
    conforme previsto na LGPD. Além disso, caso queira exercer esses direitos e excluir seus dados,
    pode também entrar em contato com nossa equipe de suporte, pelo email admin@system.com.

    5. Segurança dos Dados
    Implementamos medidas de segurança técnicas e organizacionais adequadas para proteger seus dados 
    pessoais contra acesso não autorizado, perda ou destruição.

    ----- Termos Opcionais ----- 

    6. Recebimento de Promoções e Comunicados
    Você pode optar por receber promoções, novidades e comunicados por email ou SMS. Para isso, você 
    deve autorizar explicitamente esta opção.

    7. Compartilhamento de Dados com Empresas Parceiras
    Você pode optar por permitir que seus dados sejam compartilhados com empresas parceiras para 
    ações de marketing, promoções ou ofertas personalizadas.
    
    Ao continuar, você aceita os termos obrigatórios acima. Caso deseje, poderá também aceitar 
    os termos opcionais para recebimento de promoções e compartilhamento de dados com parceiros.
    """)
    print("-------------------------\n")

def accept_terms():
    while True:
        display_terms_of_use()
        
        accept_mandatory = input("Você aceita os termos obrigatórios? (S/N): ").strip().upper()
        if accept_mandatory == 'N':
            print("Obrigado pela visita! O acesso é exclusivamente para responder à pesquisa.")
            return False, False
        elif accept_mandatory == 'S':
            accept_optional = input("Você aceita os termos opcionais (promoções por email/SMS e compartilhamento com empresas parceiras)? (S/N): ").strip().upper() == 'S'
            return True, accept_optional
        else:
            print("Opção inválida. Por favor, escolha 'S' para sim ou 'N' para não.")

def register_user(mydb):
    print("Por favor, preencha os dados abaixo para o cadastro.")
    nome = input("Nome: ")
    sobrenome = input("Sobrenome: ")
    telefone = input("Telefone (com DDD): ")
    email = input("Email: ")
    senha = input("Senha (6 dígitos): ")

    while len(senha) != 6 or not senha.isdigit():
        print("A senha deve ter exatamente 6 dígitos.")
        senha = input("Senha (6 dígitos): ")

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
    
    print("Escolha o seu bairro:")
    for i, bairro in enumerate(bairros, 1):
        print(f"{i}. {bairro}")
    
    bairro_index = int(input("Digite o número correspondente ao seu bairro: "))
    bairro = bairros[bairro_index - 1] if 1 <= bairro_index <= len(bairros) else None

    if not bairro:
        print("Bairro inválido.")
        return None

    if mydb:
        with mydb.cursor() as cursor:
            cursor.execute("USE surveydb")
            sql_user = "INSERT INTO user_login (nome, sobrenome, telefone, email, password, bairro) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql_user, (nome, sobrenome, telefone, email, senha, bairro))
            mydb.commit()
            print(f"Usuário {nome} {sobrenome} cadastrado com sucesso!")
            user_id = cursor.lastrowid
            return user_id
    else:
        print("Erro ao conectar ao banco de dados.")
        return None

def login_user(mydb):
    email = input("Email: ")
    senha = input("Senha: ")
    
    if mydb:
        with mydb.cursor() as cursor:
            cursor.execute("USE surveydb")
            cursor.execute("SELECT id FROM user_login WHERE email = %s AND password = %s", (email, senha))
            user_id = cursor.fetchone()
    
    return user_id['id'] if user_id else None

def is_admin(user_id, mydb):
    if mydb:
        with mydb.cursor() as cursor:
            cursor.execute("USE surveydb")
            cursor.execute("SELECT role FROM user_login WHERE id = %s", (user_id,))
            result = cursor.fetchone()
        return result and result['role'] == 'admin'
    return False

def main(tunnel, mydb):
    if mydb:
        try:
            while True:
                action = input("Você é um novo usuário ou deseja fazer login? (novo/login): ").strip().lower()
                if action == 'novo':
                    accepted, accept_optional = accept_terms()
                    if accepted:
                        user_id = register_user(mydb)  # Passa a conexão
                        if user_id:
                            print("Você aceitou os termos opcionais:", "Sim" if accept_optional else "Não")
                            create_survey_response(user_id, mydb)
                    else:
                        break
                elif action == 'login':
                    user_id = login_user(mydb)  # Passa a conexão
                    if user_id:
                        if is_admin(user_id, mydb):  # Passa a conexão
                            admin_main(mydb)  # Passa a conexão para a função de admin
                        else:
                            option = input("Você deseja [editar] suas respostas ou [sair]? ").strip().lower()
                            if option == 'editar':
                                user_menu(user_id, mydb)  # Passa a conexão para o menu de usuário
                            elif option == 'sair':
                                print("Saindo do sistema...")
                                break
                else:
                    print("Opção inválida. Tente novamente.")
        finally:
            pass

if __name__ == "__main__":
    main()
