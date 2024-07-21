import pytest # pytest module for testing
import sys # sys module provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter
import logging # logging module defines functions and classes which implement a flexible event logging system for applications and libraries
import time # time module provides various time-related functions
import threading # threading module constructs higher-level threading interfaces on top of the lower level thread module
from Veeam_source.veeam_task import register_setup, sync_folders, main # importing functions from veeam_task.py

@pytest.fixture # pytest.fixture decorator allows us to avoid code duplication and share objects across multiple tests
def source_folder(tmp_path): # source_folder fixture to create a source folder for testing
    source = tmp_path / "source" # source folder path set to source variable
    source.mkdir() # creating source folder
    return source # returning source folder path

@pytest.fixture # pytest.fixture decorator allows us to avoid code duplication and share objects across multiple tests
def replica_folder(tmp_path): # replica_folder fixture to create a replica folder for testing
    replica = tmp_path / "replica" # replica folder path set to replica variable
    replica.mkdir() # creating replica folder
    return replica  # returning replica folder path

@pytest.fixture # pytest.fixture decorator allows us to avoid code duplication and share objects across multiple tests
def log_file(tmp_path): # log_file fixture to create a log file for testing
    return tmp_path / "test_log.txt" # returning log file path

@pytest.fixture # pytest.fixture decorator allows us to avoid code duplication and share objects across multiple tests
def logger(log_file): # logger fixture to create a logger for testing
    return register_setup(log_file) # returning logger

def test_register_setup(log_file): # test_register_setup function to test register_setup function
    logger = register_setup(log_file) # logger variable set to register_setup function with log_file as argument
    assert logger.name == 'Veeam_logger' # checking if logger name is 'Veeam_logger' through assert statement
    assert logger.level == logging.INFO # checking if logger level is logging.INFO through assert statement

def test_sync_folders(source_folder, replica_folder, logger): # test_sync_folders function to test sync_folders function
    test_file = source_folder / "test.txt" # test_file variable set to test.txt file in source folder
    test_file.write_text("This is a test file.") # writing text to test_file
    sync_folders(source_folder, replica_folder, logger) # calling sync_folders function with source_folder, replica_folder and logger as arguments
    assert (replica_folder / "test.txt").exists() # checking if test.txt file exists in replica folder through assert statement


def test_main(monkeypatch, tmp_path): # test_main function to test main function. 
    source_folder = tmp_path / "source" # source_folder variable set to source folder path
    source_folder.mkdir() # creating source folder
    replica_folder = tmp_path / "replica" # replica_folder variable set to replica folder path
    interval = 1 # interval variable set to 1
    log_file = tmp_path / "test_log.txt" # log_file variable set to log file path

    args = [str(source_folder), str(replica_folder), str(interval), str(log_file)] # args variable set to list of source_folder, replica_folder, interval and log_file
    monkeypatch.setattr(sys, 'argv', ['Veeam_source/veeam_task.py'] + args) # setting sys.argv to list of veeam_task.py and args

    stop_event = threading.Event() # stop_event variable set to threading.Event(). this serves as a flag to stop the main function

    def run_main(): # run_main function to run main function. this is used to run main function in a separate thread
        try: # try block to run main function
            main(stop_event) # calling main function with stop_event as argument
        except SystemExit: # except block to catch SystemExit exception if something goes wrong
            pass

    thread = threading.Thread(target=run_main) # thread variable set to threading.Thread with run_main as target
    thread.start() # starting thread
    time.sleep(2)  # sleeping for 2 seconds


    stop_event.set() # setting stop_event to stop the main function
    thread.join() # joining thread