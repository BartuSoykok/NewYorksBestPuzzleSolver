import logging
import os.path
import Configs

if not os.path.exists("logs/"):
    os.makedirs("logs/")

logger = logging.basicConfig(format='%(asctime)s %(message)s', filename='logs/trials.log', level=logging.DEBUG)


def log(message):
    try:
        if Configs.get_setting('DEBUG', 'log') == '1':
            logging.info(message)
    except Exception as e:
        print(e)
