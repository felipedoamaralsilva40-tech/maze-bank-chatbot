#bibliotecas usadas no projeto
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pandas as pd
import json


perguntas = pd.read_csv("pergunta.csv")
frase = perguntas['frase'].astype(str).tolist()
categoria = perguntas['categoria'].astype(str).tolist()

#VETORIZAÇÃO E TREINAMENTO
vetorizador = CountVectorizer()
X = vetorizador.fit_transform(frase)

modelo = MultinomialNB()
modelo.fit(X, categoria)


#RESPOSTAS
with open('resposta.json', 'r') as arquivo:
  respostas = json.load(arquivo)


#CHATBOT
print('='*35)
print('  * CHATBOT - OPERADORA DE CARTÃO *  ')
print("Digite sua pergunta ou 'sair' para encerrar")
print('='*35)

while True:
  pergunta = input('\nVocê: ').lower()

  if pergunta == 'sair':
    print('Chatbot: Atendimento encerrado.')
    break

  pergunta_vetorizada = vetorizador.transform([pergunta])


  categoria_prevista = modelo.predict(pergunta_vetorizada)[0]
  
  probabilidades = modelo.predict_proba(pergunta_vetorizada)[0]
  

  maior_probabilidade = max(probabilidades)

  if maior_probabilidade < 0.60:
    print("Chatbot: Desculpe, não entendi sua solicitação. Pode reformular a pergunta?")
  else:
    print("Categoria identificada:", categoria_prevista)
    print("Probabilidade:", round(maior_probabilidade * 100, 2), "%")
    print("Chatbot:", respostas[categoria_prevista])