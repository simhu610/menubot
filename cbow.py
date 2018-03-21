# This Python file uses the following encoding: utf-8
from six.moves import cPickle as pickle
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

with open('dic_revdic_embed_weight_bias.pickle', 'rb') as f:
    my_object = pickle.load(f)

dictionary = my_object['dictionary']
reverse_dictionary = my_object['reverse_dictionary']
embeddings = my_object['embeddings']
weights = my_object['weights']
biases = my_object['biases']


def strip(w):
    chars = ".!-:;()'"
    for c in chars:
        w = w.replace(c, '')
    return w


def get_context_words(words, i):
    w = [words[i - 2],
         words[i - 1],
         words[i + 1],
         words[i + 2]]
    for i in range(len(w)):
        w[i] = strip(w[i])
    return w


def replace_words(sentence):
    words = sentence.lower().split()
    words_case = sentence.split()
    num_replaced_words = 0
    for i in range(2, len(words) - 2):
        if words[i] not in dictionary and strip(words[i]) not in dictionary:
            context_words = get_context_words(words, i)
            if all([context_word in dictionary for context_word in context_words]):
                context_words = [[dictionary[w] for w in context_words]]
                with tf.Session():
                    embed = tf.nn.embedding_lookup(embeddings, context_words)
                    averaged = tf.reduce_mean(embed, axis=1)
                    res = tf.matmul(weights, tf.transpose(averaged))
                    res = tf.reshape(res, [res.shape[0]]) + biases
                    out = tf.argmax(res).eval()
                    if reverse_dictionary[out] != "UNK":
                        if words_case[i].isupper():
                            words_case[i] = reverse_dictionary[out].upper()
                        elif words_case[i].istitle():
                            words_case[i] = reverse_dictionary[out].title()
                        else:
                            words_case[i] = reverse_dictionary[out]
                        num_replaced_words += 1
    sentence = " ".join(words_case)
    return sentence, num_replaced_words


if __name__ == "__main__":

    # sentence = "We XXXpropose two novel model architectures for computing continuous vector representations of words from very XXXlarge data sets."

    import sys
    sentence = " ".join(sys.argv[1:])

    new_sentence, num_replaced_words = replace_words(sentence)

    print sentence
    print new_sentence
    print num_replaced_words
