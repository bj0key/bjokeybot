import logging

FORMAT = "[%(asctime)s][%(funcName)s] %(levelname)s: %(message)s"


def init_logger() -> logging.Logger:
    "Initialise our logger."

    # log = logging.getLogger(LOG_NAME)
    log.addHandler(logging.FileHandler("latest.log", "w"))
    log.addHandler(logging.StreamHandler())
    log.setLevel("INFO")
    for h in log.handlers:
        h.formatter = logging.Formatter(FORMAT)

    log.debug("Logger initialied.")
    return log


log = logging.getLogger("bjokeybot")

if __name__ == "__main__":
    l = init_logger()
    l.info("haii")
