#/usr/bin/env python3
# _*_ coding: utf-8 _*_
import os
import sys
import logging

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

LOG_TYPES = {
    'transaction': 'transactions.log',
    'server': 'server.log',
}

def logger(log_type):
    #create logger
    logger = logging.getLogger(log_type)
    logger.setLevel(logging.INFO)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # create file handler and set level to warning
    log_file = os.path.join(base_dir, "logs", LOG_TYPES[log_type])
    fh = logging.FileHandler(log_file,encoding="utf-8")

    fh.setLevel(logging.INFO)
    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(thread)d %(module)s: %(message)s')

    # add formatter to ch and fh
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # add ch and fh to logger
    #logger.addHandler(ch)
    logger.addHandler(fh)

    return logger