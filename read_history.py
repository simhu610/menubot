# This Python file uses the following encoding: utf-8
import cPickle

messages = cPickle.load(open("messages_C3W65FLP4.txt", 'rb'))

print "messages", len(messages)

keys = []

for m in messages:
    for key in m.keys():
        if not key in keys:
            keys.append(key)

print "keys", len(keys)
print keys

features = []
labels = []

for m in messages:
    if 'reactions' in m:
        labels.append(m['reactions'][0]['name'])
        features.append(m['text'])
        # if len(m['reactions']) > 1:
        #     words = m['text'].split()
        #     for i, r in enumerate(m['reactions'][1:]):
        #         if len(words) > i + 1:
        #             labels.append(r['name'])
        #             feature = " ".join(words[i+1:])
        #             features.append(feature)
        # max_count = 0
        # for r in m['reactions']:
        #     if r['count'] > max_count:
        #         max_count = r['count']
        #         best = r['name']
    else:
        labels.append('NO_REACTION')
        features.append(m['text'])

from collections import Counter
print Counter(labels)

from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer()

from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
# clf = GridSearchCV(SVC(), param_grid={'C':[1, 2, 5, 10, 100, 1000, 10000, 100000], 'kernel': ['rbf', 'linear', 'poly', 'sigmoid']})
from sklearn.tree import DecisionTreeClassifier
clf = GridSearchCV(DecisionTreeClassifier(), param_grid={'min_samples_split': range(2,8)})

from sklearn.model_selection import cross_val_score
print cross_val_score(clf, vectorizer.fit_transform(features), labels)

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(features, labels)
print "train", Counter(y_train)
print "test", Counter(y_test)
features_vectorized = vectorizer.fit_transform(X_train)
clf.fit(features_vectorized, y_train)
if isinstance(clf, GridSearchCV):
    print clf.best_params_

print "train predict", Counter(clf.predict(vectorizer.transform(X_train)))
print "test predict", Counter(clf.predict(vectorizer.transform(X_test)))

for a in zip(X_test, y_test, clf.predict(vectorizer.transform(X_test))):
    if a[2] != u'NO_REACTION':
        print a

cPickle.dump({'vectorizer': vectorizer, 'svc': clf}, open("vectorizer_svc2.txt", 'wb'))
