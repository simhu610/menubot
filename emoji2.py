# This Python file uses the following encoding: utf-8
import cPickle, sys

if len(sys.argv) == 2:
    vectorizer_svc = cPickle.load(open("vectorizer_svc2.txt", 'rb'))
    vectorizer = vectorizer_svc['vectorizer']
    svc = vectorizer_svc['svc']
    text = sys.argv[1]
    print text
    print svc.predict(vectorizer.transform([text]))
