# This Python file uses the following encoding: utf-8
import sys
from menubot import get_response

if __name__ == "__main__":
    if len(sys.argv) == 2:
        print get_response(sys.argv[1])
