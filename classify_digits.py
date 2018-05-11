# This Python file uses the following encoding: utf-8
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from download_image import download_file_to_tmp
from PIL import Image
import numpy as np


def load_graph(frozen_graph_filename):
    with tf.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(
            graph_def,
            input_map=None,
            return_elements=None,
            name="prefix",
            op_dict=None,
            producer_op_list=None
        )
    return graph


def classify_digit(image_url):
    filename = download_file_to_tmp(image_url)

    if filename is not None:

        img = Image.open(filename).convert('L').resize((32, 32), Image.ANTIALIAS)
        img = np.asarray(img, dtype=np.float).reshape((1, 32, 32, 1))

        l_input = graph.get_tensor_by_name('prefix/input:0')
        l_output = graph.get_tensor_by_name('prefix/output:0')

        with tf.Session(graph=graph) as session:
            feed_dict = {l_input: img}
            output = session.run(l_output, feed_dict=feed_dict)
            output = output[0]

            for i, x in enumerate(output):
                if x > 0.5:
                    return i

    return None


graph = load_graph("hackathon_svhn_model_graph_90_3.pb")
