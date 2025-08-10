import logging




def customLogger()-> logging :
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter(
        "{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
