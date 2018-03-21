# This Python file uses the following encoding: utf-8
from six.moves import cPickle as pickle
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

MIN_SIMILARITY = 0.5

with open('dic_revdic_embed.pickle', 'rb') as f:
    my_object = pickle.load(f)

dictionary = my_object['dictionary']
reverse_dictionary = my_object['reverse_dictionary']
embeddings = my_object['embeddings']


def replace_words(sentence):

    my_dataset = [dictionary[word.lower()] for word in sentence.split() if word.lower() in dictionary]

    with tf.Session():

        norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keepdims=True))
        normalized_embeddings = embeddings / norm
        valid_embeddings = tf.nn.embedding_lookup(normalized_embeddings, my_dataset)
        similarity = tf.matmul(valid_embeddings, tf.transpose(normalized_embeddings))

        sim = similarity.eval()

    new_words = []
    num_replaced_words = 0

    for old_word in sentence.split():
        close_word = None
        if old_word.lower() in dictionary:
            dict_old_word = dictionary[old_word.lower()]
            i = my_dataset.index(dict_old_word)
            nearest = (-sim[i, :]).argsort()[1]
            if sim[i, nearest] > MIN_SIMILARITY:
                close_word = reverse_dictionary[nearest]
        if close_word is not None:
            if old_word.isupper():
                new_words.append(close_word.upper())
            elif old_word.istitle():
                new_words.append(close_word.title())
            else:
                new_words.append(close_word)
            num_replaced_words += 1
        else:
            new_words.append(old_word)

    new_sentence = " ".join(new_words)

    return new_sentence, num_replaced_words


if __name__ == "__main__":

#    sentence = "We propose two novel model architectures for computing continuous vector representations of words from very large data sets."

    import sys
    sentence = " ".join(sys.argv[1:])

    new_sentence = replace_words(sentence)

    print(sentence)
    print(new_sentence)
