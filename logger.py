import yaml
import os
import logging.config
path = "./logging.yml"
log_folder = "./log"


def setup_logging():
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)
