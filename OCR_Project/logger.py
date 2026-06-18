import logging

logging.basicConfig(
    filename="process.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def log(msg):
    logging.info(msg)
    print(msg)

def warn(msg):
    logging.warning(msg)
    print("!", msg)

def error(msg):
    logging.error(msg)
    print("X", msg)