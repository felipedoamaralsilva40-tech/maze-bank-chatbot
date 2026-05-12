from flask import Flask, request, jsonify, render_template
import sqlite3
from ia import responder

app = Flask(__name__)

def conectar():
    return sqlite3.connect("banco.db")

sessao = {}

@app.route("/")
def home():
    return render_template("maze.html")

@app.route("/chat", methods=["POST"])
def chat():

    data = request.json
    msg = data.get("pergunta", "").strip()

    user = "user"

    if user not in sessao:
        sessao[user] = {
            "estado": "cpf",
            "dados": {}
        }

    estado = sessao[user]["estado"]

    conn = conectar()
    cursor = conn.cursor()

    # LOGIN CPF
    if estado == "cpf":

        cursor.execute(
            "SELECT * FROM usuarios WHERE cpf = ?",
            (msg,)
        )

        u = cursor.fetchone()

        if u:
            sessao[user]["estado"] = "logado"

            return jsonify({
                "resposta": f"Bem-vindo de volta {u[1]} "
            })

        else:
            sessao[user]["estado"] = "nome"

            sessao[user]["dados"]["cpf"] = msg

            return jsonify({
                "resposta": "CPF não encontrado. Digite seu nome:"
            })

    # CADASTRO
    if estado == "nome":
        sessao[user]["dados"]["nome"] = msg
        sessao[user]["estado"] = "email"

        return jsonify({
            "resposta": "Digite seu email:"
        })

    if estado == "email":
        sessao[user]["dados"]["email"] = msg
        sessao[user]["estado"] = "senha"

        return jsonify({
            "resposta": "Crie uma senha:"
        })

    if estado == "senha":
        sessao[user]["dados"]["senha"] = msg
        sessao[user]["estado"] = "profissao"

        return jsonify({
            "resposta": "Digite sua profissão:"
        })

    if estado == "profissao":
        sessao[user]["dados"]["profissao"] = msg
        sessao[user]["estado"] = "telefone"

        return jsonify({
            "resposta": "Digite seu telefone:"
        })

    if estado == "telefone":

        dados = sessao[user]["dados"]

        cursor.execute("""
            INSERT INTO usuarios
            (nome, email, senha, cpf, profissao, telefone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            dados["nome"],
            dados["email"],
            dados["senha"],
            dados["cpf"],
            dados["profissao"],
            msg
        ))

        conn.commit()

        sessao[user]["estado"] = "logado"

        return jsonify({
            "resposta": f"Cadastro concluído! Bem-vindo {dados['nome']}"
        })

    # CHAT IA
    if estado == "logado":

        resposta_ia = responder(msg)

        return jsonify({
            "resposta": resposta_ia
        })

    return jsonify({
        "resposta": "Erro no sistema."
    })

if __name__ == "__main__":
    app.run(debug=True)
