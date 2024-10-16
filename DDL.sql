CREATE DATABASE IF NOT EXISTS surveydb;
USE surveydb;

-- Tabela para login
CREATE TABLE IF NOT EXISTS user_login (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    sobrenome VARCHAR(100) NOT NULL,
    telefone VARCHAR(15),
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(6) NOT NULL,
    bairro VARCHAR(100) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    is_default_admin BOOLEAN DEFAULT FALSE,
    terms_mandatory_accepted BOOLEAN DEFAULT FALSE,
    terms_optional_accepted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para respostas da pesquisa
CREATE TABLE IF NOT EXISTS survey_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user_login(id) ON DELETE CASCADE
);

-- Tabelas para Termos de uso
CREATE TABLE IF NOT EXISTS terms_of_use (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version CHAR(4) NOT NULL UNIQUE,
    terms TEXT NOT NULL,
    optional_terms TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para aceitar os termos de uso
CREATE TABLE IF NOT EXISTS user_terms_acceptance (
    user_id INT,
    terms_version CHAR(4) DEFAULT '0000',
    accepted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, terms_version),
    FOREIGN KEY (user_id) REFERENCES user_login(id) ON DELETE CASCADE,
    FOREIGN KEY (terms_version) REFERENCES terms_of_use(version)
);
