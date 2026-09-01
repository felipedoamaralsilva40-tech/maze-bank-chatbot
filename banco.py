import sqlite3


def criar_banco():

    conn = sqlite3.connect("banco.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            data_nascimento TEXT NOT NULL,
            profissao TEXT NOT NULL,
            telefone TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

    print("Banco criado com sucesso!")


if __name__ == "__main__":
    criar_banco()