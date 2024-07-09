import argparse
import os
import shutil
import sys
import logging
import time
import threading
import requests

def register_setup(log_file):
    logger = logging.getLogger('Veeam_logger')
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(log_file)
    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

def sync_folders(source_folder, replica_folder, logger):
    if not os.path.exists(replica_folder):
        os.makedirs(replica_folder)
    logger.info(f"Syncing folders: {source_folder} -> {replica_folder}")

    source_paths = set()
    for root, dirs, files in os.walk(source_folder):
        relative_path_to_root = os.path.relpath(root, source_folder)
        source_paths.add(relative_path_to_root)
        for file in files:
            source_paths.add(os.path.join(relative_path_to_root, file))

    for root, dirs, files in os.walk(replica_folder, topdown=False):
        relative_path_to_root = os.path.relpath(root, replica_folder)
        source_root = os.path.join(source_folder, relative_path_to_root)

        for filename in files:
            replica_file = os.path.join(root, filename)
            relative_file = os.path.join(relative_path_to_root, filename)
            if relative_file not in source_paths:
                try:
                    os.remove(replica_file)
                    logger.info(f"Removing file {replica_file}")
                except Exception as e:
                    logger.error(f"Error removing file {replica_file}: {e}")

        for dirname in dirs:
            replica_dir = os.path.join(root, dirname)
            relative_dir = os.path.join(relative_path_to_root, dirname)
            if relative_dir not in source_paths:
                try:
                    shutil.rmtree(replica_dir)
                    logger.info(f"Removing directory {replica_dir}")
                except Exception as e:
                    logger.error(f"Error removing directory {replica_dir}: {e}")

    logger.info(f"Removed files and directories from {replica_folder} that are not in the source folder.")

    for root, dirs, files in os.walk(source_folder):
        relative_path_to_root = os.path.relpath(root, source_folder)
        replica_root = os.path.join(replica_folder, relative_path_to_root)

        for dirname in dirs:
            dir_replica = os.path.join(replica_root, dirname)
            if not os.path.exists(dir_replica):
                os.makedirs(dir_replica)
                logger.info(f"Creating directory {dir_replica}")
            else:
                logger.info(f"Directory {dir_replica} already exists")

        for filename in files:
            source_file = os.path.join(root, filename)
            replica_file = os.path.join(replica_root, filename)
            if (not os.path.exists(replica_file) or 
                os.path.getmtime(source_file) > os.path.getmtime(replica_file)):
                try:
                    shutil.copy2(source_file, replica_file)
                    logger.info(f"Copying file {source_file} to {replica_file}")
                except Exception as e:
                    logger.error(f"Error copying {source_file} to {replica_file}: {e}")

    logger.info(f"Synchronized {source_folder} with {replica_folder}.")

#def signal_handler(sig, frame):
#    logging.info("Signal handler called with signal: {}".format(sig))
#    sys.exit(0)
    

def main(stop_event):

    #signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser(description='This synchronizes folders periodically')
    parser.add_argument('source_folder', type=str, help='Source folder to synchronize with replica folder')
    parser.add_argument('replica_folder', type=str, help='Replica folder to be synchronized with source folder')
    parser.add_argument('interval', type=int, help='Interval time in seconds for synchronization')
    parser.add_argument('log_file', type=str, help='Log file to record the synchronization')
    args = parser.parse_args()

    if not os.path.exists(args.source_folder):
        print(f"Source folder {args.source_folder} does not exist.")
        sys.exit(1)
    if not os.path.exists(args.replica_folder):
        os.makedirs(args.replica_folder)
        print(f"Created replica folder {args.replica_folder}.")
    
    logger = register_setup(args.log_file)
    logger.info(f"Starting the synchronization of {args.source_folder} with {args.replica_folder} every {args.interval} seconds.")

    while not stop_event.is_set():
        sync_folders(args.source_folder, args.replica_folder, logger)
        time.sleep(args.interval)

if __name__ == '__main__':
    stop_event = threading.Event()
    try:
        main(stop_event)
    except KeyboardInterrupt:
        stop_event.set()







