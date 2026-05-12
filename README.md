# maze-bank-chatbot
grupo
Felipe do Amaral Silva RA:2431886
Felipe Gomes RA:2428920
João Manuel Ferreia Simões Ra:2389103
Prdro Augusto Alves Romano Ra:2317875


from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pandas as pd
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
