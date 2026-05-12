from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

import pandas as pd
import sqlite3
import json

app = Flask(__name__)
CORS(app)

# BANCO
def conectar():
    return sqlite3.connect("banco.db")

# IA
perguntas = pd.read_csv("pergunta.csv")

frases = perguntas['frase'].astype(str).tolist()
categorias = perguntas['categoria'].astype(str).tolist()

vetorizador = CountVectorizer()
X = vetorizador.fit_transform(frases)

modelo = MultinomialNB()
modelo.fit(X, categorias)

with open("resposta.json", "r", encoding="utf-8") as arquivo:
    respostas = json.load(arquivo)

sessao = {}

# PÁGINA
@app.route("/")
def home():
    return render_template("maze.html")

# CHAT
@app.route("/chat", methods=["POST"])
def chat():

    data = request.json
    msg = data.get("pergunta", "").strip().lower()

    user = request.remote_addr

    if user not in sessao:
        sessao[user] = {
            "estado": "inicio",
            "dados": {}
        }

    estado = sessao[user]["estado"]

    conn = conectar()
    cursor = conn.cursor()

    # MENU INICIAL
    if estado == "inicio":

        if msg == "1":

            sessao[user]["estado"] = "cpf"

            return jsonify({
                "resposta": "Digite seu CPF:"
            })

        elif msg == "2":

            sessao[user]["estado"] = "cadastro_cpf"

            return jsonify({
                "resposta":
                "Vamos criar sua conta \n\nDigite seu CPF:"
            })

        else:

            return jsonify({
                "resposta":
                "Bem-vindo ao Maze Bank \n\n"
                "1 - Entrar\n"
                "2 - Criar conta"
            })

    # CPF CADASTRO
    if estado == "cadastro_cpf":

        sessao[user]["dados"]["cpf"] = msg

        sessao[user]["estado"] = "nome"

        return jsonify({
            "resposta": "Digite seu nome:"
        })

    
    # LOGIN CPF
    if estado == "cpf":

        cursor.execute(
            "SELECT * FROM usuarios WHERE cpf = ?",
            (msg,)
        )

        usuario = cursor.fetchone()

        if usuario:

            sessao[user]["estado"] = "logado"

            return jsonify({
                "resposta": f"Bem-vindo de volta {usuario[1]}"
            })

        else:

            return jsonify({
                "resposta":
                "CPF não encontrado.\n\n"
                "Digite 2 para criar conta."
            })
        
    # CADASTRO
    if estado == "nome":

        sessao[user]["dados"]["nome"] = msg
        sessao[user]["estado"] = "email"

        return jsonify({"resposta": "Digite seu email:"})

    if estado == "email":

        sessao[user]["dados"]["email"] = msg
        sessao[user]["estado"] = "senha"

        return jsonify({"resposta": "Crie uma senha:"})

    if estado == "senha":

        sessao[user]["dados"]["senha"] = msg
        sessao[user]["estado"] = "profissao"

        return jsonify({"resposta": "Digite sua profissão:"})

    if estado == "profissao":

        sessao[user]["dados"]["profissao"] = msg
        sessao[user]["estado"] = "telefone"

        return jsonify({"resposta": "Digite seu telefone:"})

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

    # IA

    if estado == "logado":

        pergunta_vetorizada = vetorizador.transform([msg])

        categoria_prevista = modelo.predict(pergunta_vetorizada)[0]

        probabilidades = modelo.predict_proba(pergunta_vetorizada)[0]

        if max(probabilidades) < 0.60:
            return jsonify({"resposta": "Desculpe, não entendi sua solicitação."})

        return jsonify({
            "resposta": respostas[categoria_prevista]
        })

    return jsonify({"resposta": "Erro no sistema."})


if __name__ == "__main__":
    app.run(debug=True)