#日誌紀錄，用來管理一般資訊(Log)和報錯(error)
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