import sqlite3

conn = sqlite3.connect("banco.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM usuarios")
dados = cursor.fetchall()

print("\n=== USUÁRIOS CADASTRADOS ===\n")

for d in dados:
    print(d)

conn.close()