import logging
import sys
from colorama import Fore, Style, init

init(autoreset=True)


class AppLogger:
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not self.logger.handlers:

            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_handler.stream = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

            console_formatter = self.ColoredFormatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(console_formatter)

            self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger

    class ColoredFormatter(logging.Formatter):
        LOG_COLORS = {
            logging.DEBUG: Fore.CYAN,
            logging.INFO: Fore.GREEN,
            logging.WARNING: Fore.YELLOW,
            logging.ERROR: Fore.RED,
            logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
        }

        def format(self, record: logging.LogRecord) -> str:
            color = self.LOG_COLORS.get(record.levelno, Fore.WHITE)
            record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
            return super().format(record)


logger = AppLogger("app_logger").get_logger()
