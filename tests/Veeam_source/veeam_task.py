import argparse # for parsing command line arguments
import os # for interacting with the operating system
import shutil # for high-level file operations
import sys # sys module provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter
import logging # logging module defines functions and classes which implement a flexible event logging system for applications and libraries
import time # time module provides various time-related functions
import threading # threading module constructs higher-level threading interfaces on top of the lower level thread module


def register_setup(log_file): # register_setup function to set up logging
    logger = logging.getLogger('Veeam_logger') # logger variable set to logging.getLogger with 'Veeam_logger' as argument
    logger.setLevel(logging.INFO) # setting logger level to logging.INFO

    console_handler = logging.StreamHandler(sys.stdout) # console_handler variable set to logging.StreamHandler with sys.stdout as argument. stdout is used to print output to the console
    file_handler = logging.FileHandler(log_file) # file_handler variable set to logging.FileHandler with log_file as argument. log_file is used to write logs to a file
    console_handler.setLevel(logging.INFO) # setting console_handler level to logging.INFO
    file_handler.setLevel(logging.INFO) # setting file_handler level to logging.INFO

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # formatter variable set to logging.Formatter with format string as argument
    console_handler.setFormatter(formatter) # setting formatter for console_handler
    file_handler.setFormatter(formatter) # setting formatter for file_handler

    logger.addHandler(console_handler) # adding console_handler to logger
    logger.addHandler(file_handler) # adding file_handler to logger

    return logger # returning logger

def sync_folders(source_folder, replica_folder, logger): # sync_folders function to synchronize source folder with replica folder
    if not os.path.exists(replica_folder): # checking if replica folder does not exist
        os.makedirs(replica_folder) # if not, creating replica folder
    logger.info(f"Syncing folders: {source_folder} -> {replica_folder}") # logging info message declaring syncing folders

    source_paths = set() # source_paths variable set to empty set. this will store all the paths in the source folder
    for root, dirs, files in os.walk(source_folder): # iterating through source folder
        relative_path_to_root = os.path.relpath(root, source_folder) # relative_path_to_root variable set to relative path to root
        source_paths.add(relative_path_to_root) # adding relative_path_to_root to source_paths set
        for file in files: # iterating through files in source folder
            source_paths.add(os.path.join(relative_path_to_root, file)) # adding file path to source_paths set

    for root, dirs, files in os.walk(replica_folder, topdown=False): # iterating through replica folder in reverse order, down to top
        relative_path_to_root = os.path.relpath(root, replica_folder) # relative_path_to_root variable set to relative path to root
        source_root = os.path.join(source_folder, relative_path_to_root) # source_root variable set to source folder path

        for filename in files: # iterating through files in replica folder
            replica_file = os.path.join(root, filename) # replica_file variable set to replica file path
            relative_file = os.path.join(relative_path_to_root, filename) # relative_file variable set to relative file path
            if relative_file not in source_paths: # checking if relative_file is not in source_paths
                try: # try clause to remove file
                    os.remove(replica_file) # removing file
                    logger.info(f"Removing file {replica_file}") # logging info message declaring removing file
                except Exception as e: # except clause to catch exception if something goes wrong
                    logger.error(f"Error removing file {replica_file}: {e}") # logging error message if something goes wrong

        for dirname in dirs: # iterating through directories in replica folder
            replica_dir = os.path.join(root, dirname) # replica_dir variable set to replica directory path
            relative_dir = os.path.join(relative_path_to_root, dirname) # relative_dir variable set to relative directory path
            if relative_dir not in source_paths: # checking if relative_dir is not in source_paths
                try: # try clause to remove directory
                    shutil.rmtree(replica_dir) # removing directory
                    logger.info(f"Removing directory {replica_dir}") # logging info message declaring removing directory
                except Exception as e: # except clause to catch exception if something goes wrong
                    logger.error(f"Error removing directory {replica_dir}: {e}") # logging error message if something goes wrong

    logger.info(f"Removed files and directories from {replica_folder} that are not in the source folder.") # logging info message declaring removed files and directories

    for root, dirs, files in os.walk(source_folder): # iterating through source folder
        relative_path_to_root = os.path.relpath(root, source_folder) # relative_path_to_root variable set to relative path to root
        replica_root = os.path.join(replica_folder, relative_path_to_root) # replica_root variable set to replica folder path

        for dirname in dirs: # iterating through directories in source folder
            dir_replica = os.path.join(replica_root, dirname) # dir_replica variable set to replica directory path
            if not os.path.exists(dir_replica): # checking if dir_replica does not exist
                os.makedirs(dir_replica) # if not, creating dir_replica
                logger.info(f"Creating directory {dir_replica}") # logging info message declaring creating directory
            else: # else block to log info message if directory already exists
                logger.info(f"Directory {dir_replica} already exists") # logging info message declaring directory already exists

        for filename in files: # iterating through files in source folder
            source_file = os.path.join(root, filename) # source_file variable set to source file path
            replica_file = os.path.join(replica_root, filename)   # replica_file variable set to replica file path
            if (not os.path.exists(replica_file) or 
                os.path.getmtime(source_file) > os.path.getmtime(replica_file)): # checking if replica file does not exist or source file is newer than replica file
                try: # try clause to copy file
                    shutil.copy2(source_file, replica_file) # copying file
                    logger.info(f"Copying file {source_file} to {replica_file}") # logging info message declaring copying file
                except Exception as e: # except clause to catch exception if something goes wrong
                    logger.error(f"Error copying {source_file} to {replica_file}: {e}") # logging error message if something goes wrong

    logger.info(f"Synchronized {source_folder} with {replica_folder}.") # logging info message declaring synchronization complete

    

def main(stop_event):


    parser = argparse.ArgumentParser(description='This synchronizes folders periodically') # parser variable set to argparse.ArgumentParser with description as argument. this is used to parse command line arguments
    parser.add_argument('source_folder', type=str, help='Source folder to synchronize with replica folder') # adding source_folder argument to parser with name, type and help as arguments
    parser.add_argument('replica_folder', type=str, help='Replica folder to be synchronized with source folder') # adding replica_folder argument to parser with name, type and help as arguments
    parser.add_argument('interval', type=int, help='Interval time in seconds for synchronization') # adding interval argument to parser with name, type and help as arguments
    parser.add_argument('log_file', type=str, help='Log file to record the synchronization') # adding log_file argument to parser with name, type and help as arguments
    args = parser.parse_args() # args variable set to parser.parse_args()

    if not os.path.exists(args.source_folder): # checking if source folder does not exist
        print(f"Source folder {args.source_folder} does not exist.") # printing message if source folder does not exist
        sys.exit(1) # exiting the program with status code 1. Comparing to code 0, status code 1 indicates that the program ended with an error
    if not os.path.exists(args.replica_folder): # checking if replica folder does not exist
        os.makedirs(args.replica_folder) # if not, creating replica folder
        print(f"Created replica folder {args.replica_folder}.") # printing message if replica folder is created
    
    logger = register_setup(args.log_file) # logger variable set to register_setup function with log_file as argument
    logger.info(f"Starting the synchronization of {args.source_folder} with {args.replica_folder} every {args.interval} seconds.") # logging info message declaring starting synchronization

    while not stop_event.is_set(): # while loop to run until stop_event is set
        sync_folders(args.source_folder, args.replica_folder, logger) # calling sync_folders function with source_folder, replica_folder and logger as arguments
        time.sleep(args.interval) # sleeping for interval seconds. interval is defined by user

if __name__ == '__main__': # checking if script is run directly
    stop_event = threading.Event() # stop_event variable set to threading.Event(). this serves as a flag to stop the main function
    try: # try clause to run main function
        main(stop_event) # calling main function with stop_event as argument
    except KeyboardInterrupt: # except block to catch KeyboardInterrupt exception if user interrupts the program
        stop_event.set() # setting stop_event to stop the main function







