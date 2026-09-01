from flask import Flask, request, jsonify, render_template, session
import sqlite3
from werkzeug.security import generate_password_hash
from ia import responder
from datetime import datetime
import re


app = Flask(__name__)

# Troque esta chave por uma chave aleatória em produção
app.secret_key = "maze-bank-chave-secreta-123456"


# BANCO DE DADOS

def conectar():
    conn = sqlite3.connect("banco.db")
    conn.row_factory = sqlite3.Row
    return conn


# PÁGINA PRINCIPAL

@app.route("/")
def home():
    return render_template("maze.html")


# CHAT

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "resposta": "Dados inválidos."
            }), 400

        msg = str(data.get("pergunta", "")).strip()

        if not msg:
            return jsonify({
                "resposta": "Digite alguma coisa."
            }), 400


       
        # CRIA A SESSÃO
       

        if "estado" not in session:

            session["estado"] = "cpf"


        estado = session["estado"]


       
        # CPF
       

        if estado == "cpf":

            # Aceita:
            # 12345678901
            # 123.456.789-01

            cpf = (
                msg
                .replace(".", "")
                .replace("-", "")
                .replace(" ", "")
            )

            if not cpf.isdigit() or len(cpf) != 11:

                return jsonify({
                    "resposta": "CPF inválido. Digite exatamente 11 números.",
                    "campo": "cpf"
                })


            # Procura o CPF no banco

            with conectar() as conn:

                usuario = conn.execute(
                    """
                    SELECT *
                    FROM usuarios
                    WHERE cpf = ?
                    """,
                    (cpf,)
                ).fetchone()


           
            # CPF ENCONTRADO
           

            if usuario:

                session["usuario_id"] = usuario["id"]
                session["nome"] = usuario["nome"]
                session["estado"] = "logado"

                return jsonify({
                    "resposta": (
                        f"Bem-vindo de volta, "
                        f"{usuario['nome']}!\n\n"
                        f"Como posso ajudar você?"
                    ),
                    "campo": "chat"
                })


           
            # CPF NÃO ENCONTRADO
           

            else:

                # Guarda somente o CPF durante o cadastro
                session["dados"] = {
                    "cpf": cpf
                }

                session["estado"] = "nome"

                return jsonify({
                    "resposta": (
                        "CPF não encontrado.\n\n"
                        "Vamos criar sua conta!\n\n"
                        "Digite seu nome:"
                    ),
                    "campo": "nome"
                })


       
        # NOME
       

        if estado == "nome":

            if len(msg) < 2:

                return jsonify({
                    "resposta": "Digite um nome válido:",
                    "campo": "nome"
                })


            session["dados"]["nome"] = msg

            session["estado"] = "data_nascimento"

            return jsonify({
                "resposta": (
                    "Nome registrado!\n\n"
                    "Digite sua data de nascimento "
                    "(dd/mm/aaaa):"
                ),
                "campo": "data_nascimento"
            })


       
        # DATA DE NASCIMENTO
       

        if estado == "data_nascimento":

            try:

                data_nascimento = datetime.strptime(
                    msg,
                    "%d/%m/%Y"
                )

            except ValueError:

                return jsonify({
                    "resposta": (
                        "Data inválida.\n\n"
                        "Digite no formato dd/mm/aaaa:"
                    ),
                    "campo": "data_nascimento"
                })


            # Verifica se a pessoa nasceu em um ano aceitável

            ano_atual = datetime.now().year

            if data_nascimento.year < 1900 or data_nascimento.year > ano_atual:

                return jsonify({
                    "resposta": (
                        "Data de nascimento inválida. "
                        "Digite novamente:"
                    ),
                    "campo": "data_nascimento"
                })


            session["dados"]["data_nascimento"] = msg

            session["estado"] = "email"

            return jsonify({
                "resposta": "Digite seu e-mail:",
                "campo": "email"
            })


       
        # E-MAIL
       

        if estado == "email":

            email = msg.lower()


            # Validação básica

            padrao_email = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

            if not re.match(padrao_email, email):

                return jsonify({
                    "resposta": "E-mail inválido. Digite novamente:",
                    "campo": "email"
                })


            # Verifica se já existe

            with conectar() as conn:

                email_existente = conn.execute(
                    """
                    SELECT id
                    FROM usuarios
                    WHERE email = ?
                    """,
                    (email,)
                ).fetchone()


            if email_existente:

                return jsonify({
                    "resposta": (
                        "Este e-mail já está cadastrado.\n\n"
                        "Digite outro e-mail:"
                    ),
                    "campo": "email"
                })


            session["dados"]["email"] = email

            session["estado"] = "senha"

            return jsonify({
                "resposta": (
                    "Crie uma senha com pelo menos "
                    "6 caracteres:"
                ),
                "campo": "senha"
            })


       
        # SENHA
       

        if estado == "senha":

            if len(msg) < 6:

                return jsonify({
                    "resposta": (
                        "A senha precisa ter pelo menos "
                        "6 caracteres.\n\n"
                        "Digite novamente:"
                    ),
                    "campo": "senha"
                })


            # A senha é transformada em hash.
            # Não salvamos a senha original.

            senha_hash = generate_password_hash(msg)

            session["dados"]["senha"] = senha_hash

            session["estado"] = "profissao"

            return jsonify({
                "resposta": "Senha criada!\n\nDigite sua profissão:",
                "campo": "profissao"
            })


       
        # PROFISSÃO
       

        if estado == "profissao":

            if len(msg) < 2:

                return jsonify({
                    "resposta": "Digite uma profissão válida:",
                    "campo": "profissao"
                })


            session["dados"]["profissao"] = msg

            session["estado"] = "telefone"

            return jsonify({
                "resposta": (
                    "Digite seu telefone "
                    "(somente números):"
                ),
                "campo": "telefone"
            })


       
        # TELEFONE
       

        if estado == "telefone":

            telefone = (
                msg
                .replace(" ", "")
                .replace("-", "")
                .replace("(", "")
                .replace(")", "")
            )


            if not telefone.isdigit():

                return jsonify({
                    "resposta": (
                        "Telefone inválido.\n\n"
                        "Digite somente números:"
                    ),
                    "campo": "telefone"
                })


            if len(telefone) < 8 or len(telefone) > 15:

                return jsonify({
                    "resposta": (
                        "Telefone inválido.\n\n"
                        "Digite um telefone válido:"
                    ),
                    "campo": "telefone"
                })


            dados = session.get("dados", {})


            # Verifica se todos os dados existem

            campos_obrigatorios = [
                "cpf",
                "nome",
                "data_nascimento",
                "email",
                "senha",
                "profissao"
            ]

            for campo in campos_obrigatorios:

                if campo not in dados:

                    session.clear()

                    return jsonify({
                        "resposta": (
                            "O cadastro foi reiniciado. "
                            "Digite seu CPF novamente."
                        ),
                        "campo": "cpf"
                    })


           
            # SALVAR USUÁRIO
           

            try:

                with conectar() as conn:

                    # Verifica CPF novamente

                    cpf_existente = conn.execute(
                        """
                        SELECT id
                        FROM usuarios
                        WHERE cpf = ?
                        """,
                        (dados["cpf"],)
                    ).fetchone()


                    if cpf_existente:

                        session.clear()

                        return jsonify({
                            "resposta": (
                                "Este CPF já está cadastrado.\n\n"
                                "Digite seu CPF novamente."
                            ),
                            "campo": "cpf"
                        })


                    # Verifica e-mail novamente

                    email_existente = conn.execute(
                        """
                        SELECT id
                        FROM usuarios
                        WHERE email = ?
                        """,
                        (dados["email"],)
                    ).fetchone()


                    if email_existente:

                        session["estado"] = "email"

                        return jsonify({
                            "resposta": (
                                "Este e-mail já está cadastrado.\n\n"
                                "Digite outro e-mail:"
                            ),
                            "campo": "email"
                        })


                    # Insere usuário

                    cursor = conn.execute(
                        """
                        INSERT INTO usuarios
                        (
                            nome,
                            email,
                            senha,
                            cpf,
                            data_nascimento,
                            profissao,
                            telefone
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            dados["nome"],
                            dados["email"],
                            dados["senha"],
                            dados["cpf"],
                            dados["data_nascimento"],
                            dados["profissao"],
                            telefone
                        )
                    )


                    usuario_id = cursor.lastrowid


            except sqlite3.IntegrityError:

                return jsonify({
                    "resposta": (
                        "Não foi possível concluir o cadastro. "
                        "Verifique seus dados."
                    ),
                    "campo": "telefone"
                })


           
            # LOGIN AUTOMÁTICO
           

            session.clear()

            session["usuario_id"] = usuario_id
            session["nome"] = dados["nome"]
            session["estado"] = "logado"


            return jsonify({
                "resposta": (
                    "🎉 Cadastro realizado com sucesso!\n\n"
                    f"Bem-vindo ao Maze Bank, "
                    f"{dados['nome']}!\n\n"
                    "Agora você pode fazer suas perguntas."
                ),
                "campo": "chat"
            })


       
        # CHAT COM IA
       

        if estado == "logado":

            resposta_ia = responder(msg)

            return jsonify({
                "resposta": resposta_ia,
                "campo": "chat"
            })


       
        # ESTADO DESCONHECIDO
       

        session.clear()

        return jsonify({
            "resposta": (
                "A sessão foi reiniciada.\n\n"
                "Digite seu CPF novamente:"
            ),
            "campo": "cpf"
        })


    # ERRO DO SQLITE

    except sqlite3.Error as erro:

        print("Erro SQLite:", erro)

        return jsonify({
            "resposta": "Ocorreu um erro no banco de dados."
        }), 500


    # ERRO GERAL

    except Exception as erro:

        print("Erro:", erro)

        return jsonify({
            "resposta": "Ocorreu um erro no servidor."
        }), 500


# LOGOUT

@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "resposta": "Você saiu da sua conta.",
        "campo": "cpf"
    })



# REINICIAR CADASTRO / SESSÃO


@app.route("/reset", methods=["POST"])
def reset():

    session.clear()

    return jsonify({
        "resposta": (
            "Sessão reiniciada.\n\n"
            "Digite seu CPF para entrar ou criar sua conta:"
        ),
        "campo": "cpf"
    })


# INICIAR FLASK

if __name__ == "__main__":

    app.run(debug=True)