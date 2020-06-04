import numpy as np
import random
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib
import pickle


def check(X_predict):
    vectorizer = joblib.load('model/vectorizer.pkl')
    lgs = joblib.load('model/model.pkl')
    X_predict = vectorizer.transform(X_predict)
    y_predict = lgs.predict(X_predict)
    return y_predict


def getTokens(inputString):  # custom tokenizer. ours tokens are characters rather than full words
    tokens = []
    for i in inputString:
        tokens.append(i)
    return tokens


def dump(name, password):
    with open("./src/passwd", "rb") as file:
        mp = pickle.load(file)
    with open("./src/passwd", 'wb+') as file:
        mp[name] = password
        pickle.dump(mp, file)


def init(main_passwd):
    with open("./src/main_passwd", 'wb+') as file:
        pickle.dump(main_passwd, file)
    mp = {}
    with open("./src/passwd", 'wb') as file:
        pickle.dump(mp, file)


def load(main_passwd):
    with open("./src/main_passwd", 'rb') as file:
        save_main_passwd = pickle.load(file)
        if save_main_passwd != main_passwd:
            return None
    with open("./src/passwd", 'rb') as file:
        mp = pickle.load(file)
        return mp


def have_repeat_passwd():
    with open("./src/passwd", 'rb') as file:
        mp = pickle.load(file)
        li = list(mp.values())
        return len(li) - len(set(li))


# print(check(['83Ur5C(#*,2']))

# init('123')
# dump(1, 2)
# dump(2, 4)
# dump(3, 6)
# mp = load('123')
# print(mp)
# mp = load('1234')
# print(mp)
