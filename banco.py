import sqlite3

conn = sqlite3.connect("banco.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT,
    cpf TEXT UNIQUE,
    profissao TEXT,
    telefone TEXT
)
""")

conn.commit()

print("Banco criado com sucesso!")