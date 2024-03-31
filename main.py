from os import makedirs, remove, walk, path
from os.path import splitdrive, join, dirname, getsize
from shutil import disk_usage, move, copy2
from time import strftime, time
from util import Config, byte_to_gb, percent
from dateutil.relativedelta import relativedelta
from datetime import datetime
import signal, readchar


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


def create_dest_directory(dest_path):
    """
    Create the destination directory if it doesn't exist.

    Args:
        dest_path (str): The path of the destination directory to be created.

    Returns:
        bool: True if the directory was created successfully or already exists, False otherwise.
    """
    try:
        makedirs(dest_path, exist_ok=True)
        return True
    except PermissionError as e:
        logger.error(f"Unable to create destination directory, Premission Denied. {e}")
        return False
    except OSError as e:
        logger.error(f"Unable to create destination directory: {e}")
        return False
    except Exception as e:
        logger.error(e)
        return False


def handle_duplicate_files(source_file, dest_file):
    """
    Handle duplicate files found in the destination directory.

    Args:
        source_file (str): The path of the source file.
        dest_file (str): The path of the destination file.

    Returns:
        bool: True if the duplicate file was handled successfully, False otherwise.
    """
    if path.exists(dest_file):
        logger.warning(
            f"Warining: File duplication found! Source: {source_file} --- Destination: {dest_file}."
        )
        try:
            remove(source_file)
            logger.info(f"Dulicated file {source_file} has been deleted.")
            return True
        except PermissionError as e:
            logger.error(
                f"Unable to delete Source file, Permission denied. {source_file}\n{e}"
            )
            return False
        except OSError as e:
            logger.error(f"Unable to delete Source file: {source_file}\n{e}")
            return False
        except Exception as e:
            logger.error(
                f"Unknown error while deleting duplicated file. {source_file}\n{e}"
            )
            return False


def move_files(source, dest):
    """
    Move files from the source directory to the destination directory.

    Args:
        source (str): The path of the source directory.
        dest (str): The path of the destination directory.

    Returns:
        None
    """
    start_time, total_size, files_moved = time(), 0, 0
    for root_dir, sub_dirs, files in walk(source):
        sub_dirs[:] = [d for d in sub_dirs if d.lower() not in config.exclude_path]
        logger.info(config.log_separator)
        logger.info(f"Source directory: {root_dir}")
        if files == []:
            logger.info(f"No candidate file was found.")
            continue
        for file in files:
            source_file = join(root_dir, file)
            dest_file = join(dest, splitdrive(source_file)[1][1:])
            dest_path = dirname(dest_file)
            if not create_dest_directory(dest_path):
                continue
            if handle_duplicate_files(source_file, dest_file):
                continue
            try:
                move(source_file, dest_file, copy_function=copy2)
            except PermissionError as e:
                logger.error(
                    f"Unbale to move file, Premission Denied {e.filename}. {e}"
                )
                continue
            except Exception as e:
                logger.error(f"Unexpected Error in moving files, {e}")
                continue
            logger.info(f"Move: {file} -> {dest_path}")
            total_size += getsize(dest_file)
            files_moved = files_moved + 1
    run_time = time() - start_time
    total_size = byte_to_gb(total_size)
    logger.info(
        f"{files_moved} files, {total_size} GB moved, in {run_time/60:.2f} minutes"
    )


def calc_preserved_days(filedate):
    last_day = datetime(filedate.year, filedate.month, 1) + relativedelta(
        months=1, days=-1
    )
    first_day = 1
    fifteen_day = 15
    days_to_keep_files = [first_day, fifteen_day, last_day.day]
    return days_to_keep_files


def clean(folder_path):
    """
    Clean up outdated files in the specified folder.

    This function deletes files in the given folder that were not modified on the 1st,
    15th, or last day of the month within the configured number of months to keep.

    Args:
        folder_path (str): The path of the folder to clean up.

    Returns:
        None
    """
    start_time, total_size, files_deleted = time(), 0, 0
    for root_dir, sub_dirs, files in walk(folder_path):
        sub_dirs[:] = [d for d in sub_dirs if d.lower() not in config.exclude_path]
        for file in files:
            file_path = join(root_dir, file)
            try:
                file_modify_date = datetime.fromtimestamp(
                    path.getmtime(file_path)
                ).date()
            except OSError as e:
                logger.error(f"Unable to get modification date: {e}")
                continue

            days_to_keep_files = calc_preserved_days(file_modify_date)
            current_date = datetime.today().date()
            if file_modify_date.day not in days_to_keep_files:
                if file_modify_date < (
                    current_date - relativedelta(month=config.months_to_keep)
                ):
                    try:
                        file_size = path.getsize(file_path)
                        remove(file_path)
                    except PermissionError as e:
                        logger.error(f"Permission denied: Unable to delete file. {e}")
                        continue
                    except FileNotFoundError as e:
                        print(
                            f"File not found: The file '{file_path}' does not exist. {e}"
                        )
                        continue
                    except IsADirectoryError as e:
                        logger.error(
                            f"Is a directory: {file_path}. unable to delete dir. {e}"
                        )
                        continue
                    except OSError as e:
                        logger.error(f"Unable to delete file: {e}")
                        continue
                    except Exception as e:
                        logger.error(f"Unexpected error while deleting file. {e}")
                        continue
                    total_size += file_size
                    logger.info(f"File {file_path} has been deleted.")
                    files_deleted = files_deleted + 1
    run_time = time() - start_time
    total_size = byte_to_gb(total_size)
    logger.info(f"{files_deleted} files deleted, total size {total_size} GB,")


def main():
    logger.debug(config.log_separator)
    logger.debug(f"BackupManager's starting at {strftime(config.date_format)}")
    backup_usage_percent, backup_usage = backup_drive_calc()
    san_usage_percent, san_usage = san_drive_calc()
    if (backup_usage_percent > config.backup_usage_percent) and (
        backup_usage.used < san_usage.free
    ):
        move_files(config.backup_path, config.san_drive)
    elif san_usage_percent > config.san_usage_percent:
        clean(config.san_drive)
    elif (backup_usage_percent > config.backup_usage_percent) and (
        backup_usage.used > san_usage.free
    ):
        clean(config.san_drive)
        move_files(config.backup_path, config.san_drive)
    else:
        logger.info("Backup in right condition...")
        logger.debug(f"BackupManager's ending at {strftime(config.date_format)}")


def exit_handler(signum, frame):
    """
    Handle the exit signal by asking the user for confirmation.

    Args:
        signum (int): The signal number.
        frame (frame object): The current stack frame.

    Returns:
        None
    """
    messsage = "Ctrl+C was pressed. Do you really want to exit? y/n "
    print(messsage, end="", flush=True)
    respond = readchar.readchar()
    while readchar.readchar() != b"\n":
        pass
    if respond == "y":
        print("")
        exit(1)
    else:
        print("", end="\r", flush=True)
        print(" " * len(messsage), end="", flush=True)
        print("    ", end="\r", flush=True)


if __name__ == "__main__":
    config = Config()
    logger = config.logging()
    signal.signal(signal.SIGINT, exit_handler)
    main()
