import logging
import time


def get_logger():
    logger = logging.getLogger("evident-analyses")
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s - %(levelname)s] :: %(message)s"
    )
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger


def time_function(func):
    def wrapper():
        start_time = time.time()
        func()
        end_time = time.time()
        print(f"Total script time: {end_time - start_time}")
    return wrapper
