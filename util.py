import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def getenv(name):
    return os.environ.get(name)


def num2emoji(num):
    return "{}\ufe0f\u20e3".format(num)


def emoji2num(emoji):
    return int(emoji[0])
