"""
One way synchronization between files from source to destination.

Usage:
    py sync.py <source_path> <destination_path> [-i <sync_interval>] [-l <log_file_path>] [-d]

Required arguments:
  source_path        Source path directory
  destination_path   Destination path directory

Optional arguments:
  -i                 Sync interval in seconds (default: 10)
  -l                 Path to the log file (default: current_directory/sync_log.log)
  -d                 Enables debug logging level
"""

import logging
import os
import shutil
import sys
import time


def parse_args():
    if len(sys.argv) < 3:
        print(
            "Usage: py sync.py <source_path> <destination_path> [-i <sync_interval>] [-l <log_file_path>] [-d]")
        print("One way synchronization between files from source to destination.")
        print()
        print("Required arguments:")
        print("  source_path        Source path directory")
        print("  destination_path   Destination path directory")
        print()
        print("Optional arguments:")
        print("  -i                 Sync interval in seconds (default: 10)")
        print("  -l                 Path to the log file (default: current_directory/sync_log.log)")
        print("  -d                 Enables debug logging level")
        sys.exit(1)

    source_path = sys.argv[1]
    destination_path = sys.argv[2]

    sync_interval = 10
    log_file_path = os.path.join(os.getcwd(), "sync_log.log")
    debug = False

    # Process optional arguments
    i = 3

    while i < len(sys.argv):
        match sys.argv[i]:
            case "-i":
                i += 1
                if (i < len(sys.argv)):
                    try:
                        sync_interval = int(sys.argv[i])
                    except:
                        print("Error: Value for -i argument must be a number")
                        sys.exit(1)
                else:
                    print("Error: Missing value for -i argument")
                    sys.exit(1)

            case "-l":
                i += 1
                if (i < len(sys.argv)):
                    log_file_path = sys.argv[i]
                else:
                    print("Error: Missing value for -l argument")
                    sys.exit(1)

            case "-d":
                debug = True

            case _:
                print(f"Error: Unknown argument {sys.argv[i]}")
                sys.exit(1)

        i += 1

    return source_path, destination_path, sync_interval, log_file_path, debug


def setup_logger(log_file_path: str, debug: bool):
    """
    Configure the logger with the specified log file and debug level.
    """

    logging.basicConfig(level=(logging.DEBUG if debug else logging.INFO), filename=log_file_path,
                        filemode="w", format="%(asctime)s - %(levelname)s: %(message)s")

    file_handler = logging.FileHandler(log_file_path)
    console_handler = logging.StreamHandler()

    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def sync(src: str, dest: str):
    """
    Synchronize files from source directory to destination directory.
    """

    logger.debug("Syncing...")
    tic = time.perf_counter()

    for root, dirs, files in os.walk(src):

        # Create the directory tree
        for dir in dirs:
            src_path = os.path.join(root, dir)
            dest_path = os.path.join(dest, os.path.relpath(src_path, src))

            if not os.path.exists(dest_path):
                os.makedirs(dest_path, exist_ok=True)
                logger.info(
                    f"Created directory {os.path.relpath(dest_path, dest)}")

        # Copy or modify the files
        for file in files:
            src_path = os.path.join(root, file)
            dest_path = os.path.join(dest, os.path.relpath(src_path, src))

            if not os.path.exists(dest_path):
                shutil.copy2(src_path, dest_path)
                logger.info(f"Created file {os.path.relpath(src_path, src)}")

            elif os.path.getmtime(src_path) > os.path.getmtime(dest_path):
                shutil.copy2(src_path, dest_path)
                logger.info(f"Modified file {os.path.relpath(src_path, src)}")

    for root, dirs, files in os.walk(dest):

        # Remove files
        for file in files:
            dest_path = os.path.join(root, file)
            src_path = os.path.join(src, os.path.relpath(dest_path, dest))

            if not os.path.exists(src_path):
                os.remove(dest_path)
                logger.info(f"Removed file {os.path.relpath(dest_path, dest)}")

        # Remove directories
        for dir in dirs:
            dest_path = os.path.join(root, dir)
            src_path = os.path.join(src, os.path.relpath(dest_path, dest))

            if not os.path.exists(src_path):
                shutil.rmtree(dest_path)
                logger.info(
                    f"Removed directory {os.path.relpath(dest_path, dest)}")

    toc = time.perf_counter()
    logger.debug(
        f"Syncing completed successfully! Duration: {toc - tic:0.4f} seconds.")


if __name__ == "__main__":

    # Parse the arguments
    source_path, destination_path, sync_interval, log_file_path, debug = parse_args()

    # Setup the logger
    logger = setup_logger(log_file_path, debug)

    # Run syncing
    while True:
        sync(source_path, destination_path)

        time.sleep(sync_interval)
