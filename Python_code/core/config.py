import logging
import os



def setup_logger(logs_in_file=False, level=logging.DEBUG, log_file='data/logs.log'):
    logging.getLogger('obsws_python').setLevel(logging.CRITICAL)
    logging.getLogger('comtypes').setLevel(logging.CRITICAL)
    logging.getLogger('PIL').setLevel(logging.CRITICAL)
    logging.getLogger('websocket').setLevel(logging.ERROR)
    logging.getLogger('websocket._core').setLevel(logging.ERROR)

    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        filename=log_file if logs_in_file else None,
        filemode='a' if logs_in_file else None,
        encoding='utf-8' if logs_in_file else None
    )