from configparser import ConfigParser, Error
from datetime import datetime
from os import environ, pardir, path
import sys


class Config:
    def __init__(self):
        self.config = ConfigParser()
        self.config_file = path.abspath(
            path.join(path.dirname(__file__), pardir, "config.ini")
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

    @property
    def backup_path(self):
        return path.realpath(self.get("BACKUP_PATH"))

    @property
    def san_drive(self):
        return path.realpath(self.get("SAN_DRIVE"))

    @property
    def exclude_path(self):
        exclude_path_items = self.get("EXCLUDE_PATH")
        if isinstance(exclude_path_items, str):
            return [item.strip().lower() for item in exclude_path_items.split(",")]
        else:
            return exclude_path_items

    @property
    def disk_usage_percernt(self):
        return int(self.get("DISK_USAGE_PERCENT"))

    @property
    def months_to_keep(self):
        return int(self.get("MONTHS_TO_KEEP"))

    @property
    def debug(self):
        return bool(
            (
                self.get(
                    "DEBUG",
                )
            )
        )

    @property
    def log_path(self):
        return path.realpath(self.get("LOG_PATH", fallback="./logs"))

    @property
    def log_filename(self):
        log_filename_date_format = "%d-%m-%Y"
        return f"BackupManager-{datetime.now().strftime(log_filename_date_format)}.log"


config = Config()
