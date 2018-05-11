# This Python file uses the following encoding: utf-8
import os
import tempfile
import requests


def download_file(url, local_filename, basedir):
    try:
        os.stat(basedir)
    except:
        os.mkdir(basedir)
    try:
        headers = {'Authorization': 'Bearer ' + os.environ.get('SLACK_BOT_TOKEN')}
        r = requests.get(url, headers=headers)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: f.write(chunk)
    except:
        return False

    return True


def download_file_to_tmp(image_url):

    ext = image_url.split(".")[-1]

    _, filepath = tempfile.mkstemp()
    filepath = "{}.{}".format(filepath, ext)

    if download_file(image_url, filepath, os.path.dirname(filepath)):
        return filepath
    else:
        return None
