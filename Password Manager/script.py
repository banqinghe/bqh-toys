import numpy as np
import random
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib

def getTokens(inputString):
	tokens = []
	for i in inputString:
		tokens.append(i)
	return tokens

filepath = 'data_n.csv'
data = pd.read_csv(filepath,',',error_bad_lines=False, low_memory=False)

data = pd.DataFrame(data)
passwords = np.array(data)

random.shuffle(passwords)
y = [d[1] for d in passwords]

allpasswords= np.array([d[0] for d in passwords])

vectorizer = TfidfVectorizer(tokenizer=getTokens)

X = vectorizer.fit_transform(allpasswords)

joblib.dump(vectorizer, 'vectorizer.pkl')

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

lgs = LogisticRegression(penalty='l2',multi_class='ovr', max_iter = 10000)
lgs.fit(X_train, y_train)
joblib.dump(lgs,'model.pkl')
print(lgs.score(X_test, y_test))
