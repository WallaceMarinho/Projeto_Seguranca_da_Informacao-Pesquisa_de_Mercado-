CREATE DATABASE IF NOT EXISTS surveydb;
USE surveydb;

-- Tabela para login
CREATE TABLE IF NOT EXISTS user_login (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    sobrenome VARCHAR(100) NOT NULL,
    telefone VARCHAR(15) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255),
    bairro VARCHAR(100) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user' NOT NULL,
    is_default_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    provider ENUM('local', 'google') DEFAULT 'local' NOT NULL
);

-- Modificação da tabela para garantir unicidade de (type, is_current)
CREATE TABLE IF NOT EXISTS terms_and_privacy_policy (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version CHAR(4) NOT NULL,
    type ENUM('terms', 'privacy', 'optional') NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT FALSE,
    UNIQUE(version, type),
    UNIQUE(type, is_current)
);

-- Tabela para aceitar os termos e política de privacidade
CREATE TABLE IF NOT EXISTS user_terms_and_privacy_acceptance (
    user_id INT NOT NULL,
    terms_version CHAR(4) NOT NULL,
    privacy_version CHAR(4) NOT NULL,
    optional_version CHAR(4) DEFAULT NULL,
    accepted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES user_login(id) ON DELETE CASCADE,
    FOREIGN KEY (terms_version) REFERENCES terms_and_privacy_policy(version) ON DELETE CASCADE,
    FOREIGN KEY (privacy_version) REFERENCES terms_and_privacy_policy(version) ON DELETE CASCADE,
    FOREIGN KEY (optional_version) REFERENCES terms_and_privacy_policy(version) ON DELETE SET NULL
);

-- Tabela para respostas da pesquisa
CREATE TABLE IF NOT EXISTS survey_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user_login(id) ON DELETE CASCADE
);

-- Tabela para armazenar os termos opcionais e suas versões
CREATE TABLE IF NOT EXISTS optional_terms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    optional_code VARCHAR(100) NOT NULL,
    version CHAR(4) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT FALSE,
    UNIQUE(optional_code, version)
);

-- Tabela para registrar aceites de termos opcionais por usuário
CREATE TABLE IF NOT EXISTS user_optional_terms_acceptance (
    user_id INT NOT NULL,
    optional_term_id INT NOT NULL,
    accepted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, optional_term_id),
    FOREIGN KEY (user_id) REFERENCES user_login(id) ON DELETE CASCADE,
    FOREIGN KEY (optional_term_id) REFERENCES optional_terms(id) ON DELETE CASCADE
);
