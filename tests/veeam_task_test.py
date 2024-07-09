import pytest
import os
import shutil
import sys
import logging
import signal
import time
from Veeam_source import register_setup, sync_folders, signal_handler, main

@pytest.fixture
def source_folder(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    return source

@pytest.fixture
def replica_folder(tmp_path):
    replica = tmp_path / "replica"
    replica.mkdir()
    return replica

@pytest.fixture
def log_file(tmp_path):
    return tmp_path / "test_log.txt"

@pytest.fixture
def logger(log_file):
    return register_setup(log_file)

def test_register_setup(log_file):
    logger = register_setup(log_file)
    assert logger.name == 'Veeam_logger'
    assert logger.level == logging.INFO

def test_sync_folders(source_folder, replica_folder, logger):
    test_file = source_folder / "test.txt"
    test_file.write_text("This is a test file.")
    sync_folders(source_folder, replica_folder, logger)
    assert (replica_folder / "test.txt").exists()

def test_signal_handler():
    with pytest.raises(SystemExit):
        signal_handler(signal.SIGINT, None)

def test_main(monkeypatch, tmp_path):
    source_folder = tmp_path / "source"
    source_folder.mkdir()
    replica_folder = tmp_path / "replica"
    interval = 1
    log_file = tmp_path / "test_log.txt"

    args = [str(source_folder), str(replica_folder), str(interval), str(log_file)]
    monkeypatch.setattr(sys, 'argv', ['Veeam_task.py'] + args)
    
    from Veeam_source import main
    import threading

    def run_main():
        try:
            main()
        except SystemExit:
            pass

    thread = threading.Thread(target=run_main)
    thread.start()
    time.sleep(2)
    os.kill(thread.ident, signal.SIGINT)
    thread.join()

    assert os.path.exists(replica_folder)
    assert os.path.exists(log_file)
