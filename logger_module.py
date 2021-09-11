import datetime
import logging
import pathlib


def setup_logger():
    logging_path = pathlib.Path(f"./.logs")
    logging_path.mkdir(exist_ok=True)

    logger = logging.getLogger("FMEL_HOUSING")
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    fh = logging.FileHandler(
        f"./.logs/log_{str(datetime.datetime.now()).replace('.', '-').replace(':', '-').replace('/', '-')}.log",
        mode="w")
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)
