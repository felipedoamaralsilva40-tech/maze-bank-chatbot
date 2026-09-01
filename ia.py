from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pandas as pd
import json



# CARREGAR PERGUNTAS


perguntas = pd.read_csv("pergunta.csv")

frase = perguntas["frase"].astype(str).tolist()
categoria = perguntas["categoria"].astype(str).tolist()



# VETORIZAÇÃO


vetorizador = CountVectorizer()

X = vetorizador.fit_transform(frase)



# TREINAMENTO DO MODELO


modelo = MultinomialNB()

modelo.fit(X, categoria)



# CARREGAR RESPOSTAS


with open("resposta.json", "r", encoding="utf-8") as arquivo:
    respostas = json.load(arquivo)



# FUNÇÃO DO CHATBOT


def responder(pergunta):

    pergunta = str(pergunta).strip().lower()

    if not pergunta:
        return "Digite uma pergunta."


    # Transforma a pergunta em vetor
    pergunta_vetorizada = vetorizador.transform([pergunta])


    # Verifica se existem palavras conhecidas
    if pergunta_vetorizada.nnz == 0:
        return "Desculpe, não entendi sua solicitação. Pode reformular a pergunta?"


    
    # PREVISÃO
    

    categoria_prevista = modelo.predict(
        pergunta_vetorizada
    )[0]


    
    # PROBABILIDADE
    

    probabilidades = modelo.predict_proba(
        pergunta_vetorizada
    )[0]

    maior_probabilidade = max(probabilidades)


    
    # CONFIANÇA MÍNIMA
    

    if maior_probabilidade < 0.60:

        return (
            "Desculpe, não entendi sua solicitação. "
            "Pode reformular a pergunta?"
        )


    
    # BUSCAR RESPOSTA
    

    resposta = respostas.get(categoria_prevista)


    if resposta is None:

        return (
            "Encontrei sua solicitação, mas ainda "
            "não tenho uma resposta cadastrada para ela."
        )


    return resposta