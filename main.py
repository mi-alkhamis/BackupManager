from os.path import splitdrive
from shutil import disk_usage
from time import strftime
from util import Config, byte_to_gb, percent


def backup_drive_calc():
    logger.info("Calculating Disk Summary...")
    backup_usage = disk_usage(splitdrive(config.backup_path)[0])
    backup_drive = splitdrive(config.backup_path)[0]
    backup_drive_total = byte_to_gb(disk_usage(backup_drive).total)
    backup_drive_used = byte_to_gb(disk_usage(backup_drive).used)
    backup_usage_percent = percent(backup_usage.used, backup_usage.total)
    logger.info(
        f"{backup_drive} Backup Drive Usage: {backup_drive_used:.2f}/{backup_drive_total:.2f} GB - {backup_usage_percent}%"
    )
    return backup_usage_percent, backup_usage


def san_drive_calc():
    san_drive = splitdrive(config.san_drive)[0]
    san_usage = disk_usage(san_drive)
    san_drive_total = byte_to_gb(san_usage.total)
    san_drive_free = byte_to_gb(san_usage.free)
    san_free_percent = percent(san_usage.free, san_usage.total)
    logger.info(
        f"{san_drive} San Drive Free: {san_drive_free:.2f}/{san_drive_total:.2f} GB - {san_free_percent}%"
    )
    san_usage = disk_usage(splitdrive(config.san_drive)[0])
    san_usage_percent = percent(san_usage.used, san_usage.total)
    return san_usage_percent, san_usage


def main():
    logger.debug(f"BackupManager's starting at {strftime(config.date_format)}")
    backup_usage_percent, backup_usage = backup_drive_calc()
    san_usage_percent, san_usage = san_drive_calc()
    logger.debug(f"BackupManager's ending at {strftime(config.date_format)}")

if __name__ == "__main__":   
    config = Config()
    logger = config.logging()
    logger.debug(config.log_separator) 
    main()
