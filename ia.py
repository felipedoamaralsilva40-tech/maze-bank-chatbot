from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pandas as pd
import json

# carregar perguntas
perguntas = pd.read_csv("pergunta.csv")

frases = perguntas['frase'].astype(str).tolist()
categorias = perguntas['categoria'].astype(str).tolist()

# treinar modelo
vetorizador = CountVectorizer()

X = vetorizador.fit_transform(frases)

modelo = MultinomialNB()

modelo.fit(X, categorias)

# respostas
with open("resposta.json", "r", encoding="utf-8") as arquivo:
    respostas = json.load(arquivo)

# função principal
def responder(msg):

    pergunta_vetorizada = vetorizador.transform([msg])

    categoria_prevista = modelo.predict(
        pergunta_vetorizada
    )[0]

    probabilidades = modelo.predict_proba(
        pergunta_vetorizada
    )[0]

    maior_probabilidade = max(probabilidades)

    if maior_probabilidade < 0.60:
        return "Desculpe, não entendi sua solicitação."

    return respostas[categoria_prevista]