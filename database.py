import sqlite3
import os

DB_PATH = "deskbot.db"

def init_db():
    """Inicializa o banco de dados e cria as tabelas se não existirem."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabela de Automações (Manuais: Texto + Imagem)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS automacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            keyword TEXT UNIQUE,
            texto TEXT,
            caminho_imagem TEXT
        )
    ''')

    # Tabela de Resolutivas (Apenas Texto)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resolutivas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            keyword TEXT UNIQUE,
            texto TEXT
        )
    ''')

    conn.commit()
    conn.close()

def get_todas_automacoes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nome, keyword, texto, caminho_imagem FROM automacoes")
    dados = cursor.fetchall()
    conn.close()
    return dados

def get_todas_resolutivas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nome, keyword, texto FROM resolutivas")
    dados = cursor.fetchall()
    conn.close()
    return dados