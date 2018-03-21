# This Python file uses the following encoding: utf-8
from six.moves import cPickle as pickle
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
import random

with open('predict_next.pickle', 'rb') as f:
    my_object = pickle.load(f)

dictionary = my_object['dictionary']
reverse_dictionary = my_object['reverse_dictionary']
embeddings = my_object['embeddings']
weights = my_object['weights']
biases = my_object['biases']

graph = tf.Graph()
with graph.as_default(), tf.device('/cpu:0'):
    input = tf.placeholder(tf.int32, shape=[1])
    input_embed = tf.nn.embedding_lookup(embeddings, input)
    res = tf.matmul(weights, tf.transpose(input_embed))
    res = tf.reshape(res, [res.shape[0]]) + biases
    k = 10
    _, predictions = tf.nn.top_k(res, k=k)


def create_sentence(start_word):

    if start_word not in dictionary:
        return None

    word = dictionary[start_word]
    skip_list = [dictionary[w] for w in ['UNK', 'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']]
    used = []

    while True:
        used.append(word)

        with tf.Session(graph=graph) as session:
            feed_dict = {input: [word]}
            predictions_array = session.run(predictions, feed_dict=feed_dict)

        predictions_filtered = [o for o in predictions_array if
               o not in used and o not in skip_list and (len(reverse_dictionary[o]) > 1 or o == 'a' or o == 'i')]

        if len(predictions_filtered) <= 0:
            break

        word = random.sample(predictions_filtered, 1)[0]

    return " ".join([reverse_dictionary[u] for u in used])


if __name__ == "__main__":

    import sys
    start_word = " ".join(sys.argv[1:])

    print(start_word)

    start_word = start_word.split()
    if len(start_word) == 1 and start_word[0].endswith('...'):
        start_word = start_word[0][:-3]
        print(start_word)
        print create_sentence(start_word)
    elif len(start_word) == 2 and start_word[1] == '...':
        start_word = start_word[0]
        print(start_word)
        print create_sentence(start_word)
