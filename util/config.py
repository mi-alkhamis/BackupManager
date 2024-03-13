from configparser import ConfigParser, Error
from datetime import datetime
import os, sys


class Config:
    def __init__(self):
        self.config = ConfigParser()
        self.config_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir, "config.ini")
        )
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
            else:
                raise FileNotFoundError
        except ValueError as e:
            print(f"Error: Invalid path for {key} in section {section}")
            sys.exit()
        except FileNotFoundError as e:
            print(f"Error: '{path}' Path was not found! {key} in section {section}")
            sys.exit()

    def get_bolean(self, key, fallback=None, section="default"):
        try:
            return self.config.getboolean(section, key, fallback=fallback)
        except ValueError as e:
            print(f"Error: Invalid value for {key} in section {section}")
            sys.exit()

    def get_int(self, key, fallback=None, section="default"):
        try:
            return self.config.getint(section, key, fallback=fallback)
        except ValueError as e:
            print(f"Error: Invalid value for {key} in section {section}")
            sys.exit()

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
    def disk_usage_percernt(self):
        return self.get_int("DISK_USAGE_PERCENT")

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


config = Config()
