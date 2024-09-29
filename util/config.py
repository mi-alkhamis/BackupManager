import logging
import os
import sys
from configparser import ConfigParser, Error
from datetime import datetime
import coloredlogs


class Config:
    def __init__(self):
        self.config = ConfigParser()
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),os.pardir)
        self.config_file = os.path.join(base_path, "config.ini")
        self.read_config(self.config_file)

    def read_config(self, config_path):
        try:
            with open(config_path, "r") as config_file:
                self.config.read_file(config_file)
        except FileNotFoundError:
            print(f"Error: Config file not found at {config_path}")
            sys.exit(1)
        except Error as e:
            print(f"Error reading config file:\n{e}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e} at {config_path}")
            sys.exit(1)

    def get(self, key, fallback=None, section="default"):
        return self.config.get(section, key, fallback=fallback)

    def get_path(self, key, fallback=".", section="default"):
        try:
            path = self.config.get(section, key, fallback=fallback)
            if os.path.exists(path):
                return path
            os.mkdir(path)
            return path
        except ValueError as e:
            print(f"Error: Invalid path for {key} in section {section}")
            sys.exit(1)
        except FileNotFoundError as e:
            print(f"Error: '{path}' Path was not found! {key} in section {section}")
            sys.exit(1)
        except PermissionError as e:
            print(f"Error: Permission Denied. Unable to create {path}")
            sys.exit(1)

    def get_bolean(self, key, fallback=None, section="default"):
        try:
            return self.config.getboolean(section, key, fallback=fallback)
        except ValueError as e:
            print(f"Error: Invalid value for {key} in section {section}")
            sys.exit(1)

    def get_int(self, key, fallback=None, section="default"):
        try:
            return self.config.getint(section, key, fallback=fallback)
        except ValueError as e:
            print(f"Error: Invalid value for {key} in section {section}")
            sys.exit(1)

    @property
    def backup_path(self):
        return os.path.realpath(self.get_path("BACKUP_PATH"))

    @property
    def san_drive(self):
        return os.path.realpath(self.get_path("SAN_DRIVE"))

    @property
    def exclude_path(self):
        exclude_path_items = self.get("EXCLUDE_PATH")
        if isinstance(exclude_path_items, str):
            return [item.strip().lower() for item in exclude_path_items.split(",")]
        else:
            return exclude_path_items

    @property
    def backup_usage_percent(self):
        return self.get_int("BACKUP_USAGE_PERCENT")

    @property
    def san_usage_percent(self):
        return self.get_int("SAN_USAGE_PERCENT")

    @property
    def months_to_keep(self):
        return self.get_int("MONTHS_TO_KEEP")

    @property
    def debug(self):
        return self.get_bolean("DEBUG")

    @property
    def log_path(self):
        return os.path.realpath(self.get_path("LOG_PATH", fallback="./logs"))

    @property
    def log_filename(self):
        log_filename_date_format = "%d-%m-%Y"
        return f"BackupManager-{datetime.now().strftime(log_filename_date_format)}.log"

    @property
    def log_separator(self):
        log_separator = "-" * 100
        return log_separator

    def logging(self):
        logger = logging.getLogger(__name__)
        try:
            os.makedirs(config.log_path, exist_ok=True)
        except PermissionError as e:
            print(
                f"Error: Permission denied while creating log directory at {config.log_path}"
            )
            sys.exit(1)
        except OSError as e:
            print(
                f"Error: An OS error occurred while creating log directory at {config.log_path}: {e}"
            )
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1)

        log_path = os.path.join(config.log_path, config.log_filename)
        file_handler = logging.FileHandler(log_path)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] - %(message)s", datefmt=self.date_format
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logging.basicConfig(
            level=logging.DEBUG,
        )
        levelstyles = {
            "critical": {"bold": True, "color": "red"},
            "debug": {"color": "magenta"},
            "error": {"color": "red"},
            "info": {"color": "green"},
            "warning": {"color": "yellow"},
        }
        coloredlogs.install(
            logger=logger,
            fmt="%(message)s",
            level=logging.DEBUG,
            level_styles=levelstyles,
        )
        return logger

    @property
    def date_format(self):
        date_format = "%d-%m-%Y %H:%M:%S"
        return date_format


config = Config()
