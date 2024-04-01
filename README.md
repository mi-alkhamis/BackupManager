# Backup Manager
The Backup Manager is a Python script designed to automate backup operations and manage disk space usage efficiently. It provides features for calculating disk usage, moving files between directories, cleaning up outdated files, and handling exit signals gracefully.

## Features
  - Disk Summary Calculation:
      - Calculates disk usage summary for backup and SAN drives.
      - Provides insights into drive usage, including total capacity, used space, and percentage used.

  - Move Files:
      - Moves files from a source directory to a destination directory.
      - Handles duplicate files and creates destination directories if they don't exist.

  - Clean Up Outdated Files:
      - Cleans up outdated files in a specified folder.
      - Deletes files that were not modified on specific days of the month within the configured retention period.

  - Graceful Exit Handling:
      - Handles exit signals, such as Ctrl+C, by prompting the user for confirmation before exiting.

## Usage
  - Installation:
      - Clone the repository to your local machine:
          ```shell
          git clone https://github.com/mi-alkhamis/BackupManager.git
          ```

      - Navigate to the project directory:
          ```shell
          cd BackupManager
          ```
      - create a new virtual environment named `env`:
          ```bash
          python3 -m venv env
          ```
      - Activate the virtual environment. On Windows, run:
          ```bash
          .\env\Scripts\activate
          ```
          On macOS and Linux, run:
          ```bash
          source env/bin/activate
          ```
      - Install Python dependencies using pip:
          ```shell
          pip install -r requirements.txt
          ```

  - Configuration:
      - Modify the config.ini file to set up paths, exclusion criteria, retention periods, and logging configurations as per your requirements.
          ```ini
          [default]
          BACKUP_PATH=/mnt/backup_location
          SAN_DRIVE=/mnt/san_drive
          BACKUP_USAGE_PERCENT=70
          SAN_USAGE_PERCENT=80
          MONTHS_TO_KEEP=6
          DEBUG=1
          LOG_PATH=/var/log/backup_manager
          EXCLUDE_PATH=tmp,cache
          ```


  - Execution:
      - Run the main.py script to start the Backup Manager:
          ```shell
          python main.py
          ```

      - The script will calculate disk usage, perform file operations, and clean up outdated files based on the configured settings.

## Logging
  - The Backup Manager logs its activities to a log file named BackupManager-<date>.log in the specified LOG_PATH directory.
  - Log entries include timestamps, log levels (e.g., INFO, WARNING, ERROR), and descriptive messages about the script's operations.

## Contributing
  Contributions to the Backup Manager project are welcome! If you encounter any issues, have suggestions for improvements, or want to add new features, please open an issue or submit a pull request on GitHub.

## License
This project is licensed under the GNU General Public License v3.0 License. See the [LICENSE](LICENSE) file for more details..

