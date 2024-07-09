import argparse
import os
import shutil
import sys
import logging
import signal
import time
import numpy
import requests
import pytest
from unittest.mock import patch

#Fixtures

@pytest.fixture # decorator to define a fixture
def log_file(tmp_path): # fixture to create a temporary log file
    log_file_path = tmp_path / 'log.txt' # creates a path to the temporary log file
    log_file_path.write_text('Log content') # creates the temporary log file
    return log_file_path # returns the path to the temporary log file

@pytest.fixture # decorator to define a fixture
def source_folder(tmp_path): # fixture to create a temporary source folder
    source_folder_path = tmp_path / 'source_folder' # creates a path to the temporary source folder
    source_folder_path.mkdir() # creates the temporary source folder
    #adds a file to the source folder if needed
    return source_folder_path # returns the path to the temporary source folder

@pytest.fixture # decorator to define a fixture
def replica_folder(tmp_path): # fixture to create a temporary replica folder
    replica_folder_path = tmp_path / 'replica_folder' # creates a path to the temporary replica folder
    replica_folder_path.mkdir() # creates the temporary replica folder
    #adds a file to the replica folder if needed
    return replica_folder_path # returns the path to the temporary replica folder

@pytest.fixture # decorator to define a fixture
def logger(): # fixture to create a logger object
    logger = logging.getLogger('Veeam_logger') # creates a logger object
    logger.setLevel(logging.INFO) # sets the level of the logger to INFO
    return logger # returns the logger object

@pytest.fixture # decorator to define a fixture
def sig():
    return signal.SIGTERM # returns the signal SIGTERM, meaning that the signal is a termination signal

#Updating tests to use fixtures

# Logger definition and configuration to record messages either in console and in a file

def test_register_setup(log_file):
    
    logger = logging.getLogger('Veeam_logger') # created object 'logger' setting up to getlogger method from logging module.
    logger.setLevel(logging.INFO) # Defines the level of the logger to INFO, which means that only messages of this level or higher will be logged.

    # Creating a set of handlers
    console_handler = logging.StreamHandler(sys.stdout) # Creates a StreamHandler which log  pattern messages (sys.stdout) to console where the scritp is being executed.
    file_handler = logging.FileHandler(log_file) # Creates a FileHandler to log messages into a specific file. The path of the file is defined by the variable 'log_file'. This handler catches all messages and writes them into the file.
    console_handler.setLevel(logging.INFO) # Defines the level of the consoleHandler to INFO, which means that only messages of this level or higher will be logged.
    file_handler.setLevel(logging.INFO) # Defines the level of the filehandler to INFO, which means that only messages of this level or higher will be logged.

    # Creating a set of formatters adding to handlers to format messages

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Creates a formatter object to define the format of the messages that will be logged. The format is defined by the string passed as argument to the constructor. %(asctime)s is the date and time of the message, %(name)s is the name of the logger, %(levelname)s is the level of the message and %(message)s is the message itself.
    console_handler.setFormatter(formatter) # Sets the formatter to the consoleHandler. Meaning, it will associate the formatter to the previous StreamHandler.
    file_handler.setFormatter(formatter) # Sets the formatter to the filehandler. Meaning, it will associate the formatter to the previous FileHandler.

    # Adding handlers to the logger

    logger.addHandler(console_handler) # Adds the consoleHandler to the logger. Meaning, it will associate the consoleHandler to the logger. Now, every messages logged by the logger will be printed in the console.
    logger.addHandler(file_handler) # Adds the filehandler to the logger. Meaning, it will associate the filehandler to the logger. Now, every messages logged by the logger will be written in the file.

    assert log_file.exists() # Asserts that the log file exists. If it does not exist, the test will fail.
    #return logger

# function for folder synchronization

def test_sync_folders(source_folder, replica_folder, logger): # function that receives the source folder, replica folder and logger as parameters
    # This synchronizes the files and directories of the source folder with the replica folder.
    # Inicializing the source_paths set to store the paths of the source folder.
    source_paths = set() # creates a set of source folder paths
    for root, dirs, files in os.walk(source_folder): # loops through the source folder using the os module and the walk method which generates the file names in a directory tree by walking either top-down or bottom-up.
        relative_path_to_root = os.path.relpath(root, source_folder) # creates a relative path to the root of the source folder. To make sure that the path is correct, the relpath method is used, which returns a relative path from the start path to the end path.
        source_paths.add(relative_path_to_root) # adds the relative path to the root of the source folder to the sourcepaths set.
        for file in files: # loops through the files in the source folder
            source_paths.add(os.path.join(relative_path_to_root, file)) # adds the path of the file to the sourcepaths set. The join method is used to concatenate the relative path to the root with the file name.

    # looping through the replica folder to remove files and directories that are not in the source folder. Starting the structure by removing this files and directories first is very important because it ensures that the content from the source folder will be copied to the replica folder by the end of the each synchronization. Otherwise, the replica folder would end up empty.
    for root, dirs, files in os.walk(replica_folder, topdown=False): # loops through the replica folder using the os module and the walk method which generates the file names in a directory tree by walking either top-down or bottom-up.
        relative_path_to_root = os.path.relpath(root, replica_folder) # creates a relative path to the root of the replica folder. To make sure that the path is correct, the relpath method is used, which returns a relative path from the start path to the end path.
        source_root = os.path.join(source_folder, relative_path_to_root) # creates a source path to the root of the replica folder. The join method is used to concatenate the source folder with the relative path to the root.

        # Removing files from replica folder that are not in the source folder
        for filename in files: # loops through the files in the replica folder
            replica_file = os.path.join(root, filename) # creates a replica file path. The join method is used to concatenate the root with the file name.
            relative_file = os.path.join(relative_path_to_root, filename) # creates a relative file path. The join method is used to concatenate the relative path to the root with the file name.
            if relative_file not in source_paths: # checks if the relative file path is not in the source paths set
                try: # tries to remove the file
                    os.remove(replica_file) # removes the file from the replica folder
                    logger.info(f"Removing file {replica_file}") # logs the message that the file was removed
                except Exception as e: # catches an exception if the file cannot be removed
                    logger.error(f"Error removing file {replica_file}: {e}") # logs the exception error message

        # Removing directories from replica folder that are not in the source folder
        for dirname in dirs: # loops through the directories in the replica folder
            replica_dir = os.path.join(root, dirname) # creates a replica directory path. The join method is used to concatenate the root with the directory name.
            relative_dir = os.path.join(relative_path_to_root, dirname) # creates a relative directory path. The join method is used to concatenate the relative path to the root with the directory name.
            if relative_dir not in source_paths: # checks if the relative directory path is not in the source paths set
                try: # tries to remove the directory
                    shutil.rmtree(replica_dir) # removes the directory from the replica folder
                    logger.info(f"Removing directory {replica_dir}") # logs the message that the directory was removed
                except Exception as e: # catches an exception if the directory cannot be removed
                    logger.error(f"Error removing directory {replica_dir}: {e}") # logs the exception error message

    logger.info(f"Removed files and directories from {replica_folder} that are not in the source folder.") # logs the message that the files and directories were removed from the replica folder.

    # Copying all files and directories from the source folder to the replica folder
    for root, dirs, files in os.walk(source_folder): # loops through the source folder using the os module and the walk method which generates the file names in a directory tree by walking either top-down or bottom-up.
        relative_path_to_root = os.path.relpath(root, source_folder) # creates a relative path to the root of the source folder. To make sure that the path is correct, the relpath method is used, which returns a relative path from the start path to the end path.
        replica_root = os.path.join(replica_folder, relative_path_to_root) # creates a replica path to the root of the source folder. The join method is used to concatenate the replica folder with the relative path to the root.

        # Creating directories from source folder in the replica folder
        for dirname in dirs: # loops through the directories in the source folder
            dir_replica = os.path.join(replica_root, dirname) # creates a directory path in the replica folder. The join method is used to concatenate the replica root with the directory name.
            if not os.path.exists(dir_replica): # checks if the directory does not exist in the replica folder
                os.makedirs(dir_replica) # creates the directory in the replica folder
                logger.info(f"Creating directory {dir_replica}") # logs the message that the directory was created
            else: # if the directory already exists
                logger.info(f"Directory {dir_replica} already exists") # logs the message that the directory already exists

        # Copying files from source folder to the replica folder
        for filename in files: # loops through the files in the source folder
            source_file = os.path.join(root, filename) # creates a source file path. The join method is used to concatenate the root with the file name.
            replica_file = os.path.join(replica_root, filename) # creates a replica file path. The join method is used to concatenate the replica root with the file name.
            if (not os.path.exists(replica_file) or 
                os.path.getmtime(source_file) > os.path.getmtime(replica_file)): # checks if the file does not exist in the replica folder or if the modification time of the source file is greater than the modification time of the replica file
                try: # tries to copy the file
                    shutil.copy2(source_file, replica_file) # copies the file from the source folder to the replica folder. the copy2 method is used to copy the file and preserve the metadata.
                    logger.info(f"Copying file {source_file} to {replica_file}") # logs the message that the file was copied
                except Exception as e: # catches an exception if the file cannot be copied
                    logger.error(f"Error copying {source_file} to {replica_file}: {e}") # logs the exception error message

    logger.info(f"Synchronized {source_folder} with {replica_folder}.") # logs the message that the source folder was synchronized with the replica folder.

# function to handle the signal

def test_signal_handler(sig): # function that receives the signal as parameter
    # signal handler to stop the script by pressing Ctrl+C
    logger = logging.getLogger('Veeam_logger') # gets the logger object. It was inside another function previously, so it needs to be called again.
    logger.info("Received signal to stop the script.") # logs the message that the signal to stop the script was received.
    assert sig == signal.SIGTERM # asserts that the signal is equal to SIGTERM. If it is not, the test will fail.
    #sys.exit(0) # exits the script with status code 0.

def test_main(): # test the main function and its arguments.
    test_args = ["program_name", "source_folder", "replica_folder", "15", "log_file"] # creates a list of arguments to test the main function
    with patch.object(sys, 'argv', test_args): # patches the sys module and the argv attribute with the test arguments
        main() # calls the main function

# main function to configure arguments and start the synchronization process
if __name__ == '__main__': # checks if the script is being executed as the main program
    def main(): # main function
        # main function to synchronize folders periodically
        parser = argparse.ArgumentParser(description='This synchronizes folders periodically') # creates an ArgumentParser object to parse the arguments passed to the script. The description argument is used to define the description of the script.
        parser.add_argument('source_folder', type=str, help='Source folder to synchronize with replica folder') # adds an argument to the parser. The source_folder argument is the source folder to synchronize with the replica folder. The type argument is used to define the type of the argument. The help argument is used to define the help message of the argument.
        parser.add_argument('replica_folder', type=str, help='Replica folder to be synchronized with source folder') # adds an argument to the parser. The replica_folder argument is the replica folder to be synchronized with the source folder. The type argument is used to define the type of the argument. The help argument is used to define the help message of the argument.
        parser.add_argument('interval', type=int, help='Interval time in seconds for synchronization') # adds an argument to the parser. The interval argument is the interval time in seconds for synchronization. The type argument is used to define the type of the argument. The help argument is used to define the help message of the argument.
        parser.add_argument('log_file', type=str, help='Log file to record the synchronization') # adds an argument to the parser. The log_file argument is the log file to record the synchronization. The type argument is used to define the type of the argument. The help argument is used to define the help message of the argument.
        args = parser.parse_args() # parses the arguments passed to the script and stores them in the args variable.
        
        # Checking if the source folder exists and creating the replica folder if it does not exist
        if not os.path.exists(args.source_folder): # checks if the source folder does not exist
            print(f"Source folder {args.source_folder} does not exist.") # prints the message that the source folder does not exist
            sys.exit(1) # exits the script with status code 1.
        if not os.path.exists(args.replica_folder): # checks if the replica folder does not exist
            os.makedirs(args.replica_folder) # creates the replica folder
            print(f"Created replica folder {args.replica_folder}.") # prints the message that the replica folder was created
            
        logger = logging.getLogger('Veeam_logger') # creates a logger object
        logger.setLevel(logging.INFO) # sets the level of the logger to INFO can only log messages of this level or higher.
        console_handler = logging.StreamHandler(sys.stdout) # creates a StreamHandler which log  pattern messages (sys.stdout) to console where the scritp is being executed.
        file_handler = logging.FileHandler(args.log_file) # creates a FileHandler to log messages into a specific file. The path of the file is defined by the log_file argument.
        console_handler.setLevel(logging.INFO) # sets the level of the consoleHandler to INFO. Can only log messages of this level or higher.
        file_handler.setLevel(logging.INFO) # sets the level of the fileHandler to INFO. Can only log messages of this level or higher.
    
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # creates a formatter object to define the format of the messages that will be logged.
        console_handler.setFormatter(formatter) # sets the formatter to the consoleHandler.
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler) # adds the consoleHandler to the logger.
        logger.addHandler(file_handler) # adds the fileHandler to the logger.

        signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0)) # registers the signal handler to stop the script by pressing Ctrl+C

        while True: # loops indefinitely. Untill we say to stop the script by sending a signal, using the keyboard shortcut Ctrl+C in the terminal.
            try:
                test_sync_folders(args.source_folder, args.replica_folder, logger) # calls the sync_folders function passing the source folder, replica folder and logger as arguments
                time.sleep(args.interval) # sleeps the script for the interval time. The interval time is passed as an argument to the script and defined by the user. In the terminal in this case.
            except Exception as e: # catches an exception if the script cannot synchronize the folders
                logger.error(f"Error synchronizing folders: {e}")


    main() # calls the main function that makes everything work






