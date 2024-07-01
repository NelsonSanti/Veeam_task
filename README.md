# Folders Synchronization

## Description:

This project implements a program that synchronizes two folders: **"Main"** and **"Copy"**.
The aim is to maintain a *full*, *identical* copy of the **source folder** in the **replica folder** taking into account the following rules:

* The synchronization must be *one-way*: after the synchronization, the content of the replica should be modified to exactly match the content of the source folder;
* The synchronization should be performed periodically;
* The file **creation**/**copying**/**removal** operations should be logged to a file (`synchronized.log` in this exercise) and the console output;
* **Folder paths**, **synchronization interval**, and **log file path**, should be provided using the command line arguments;
* It is undesirable to use third-party libraries that implement folder synchronization;
* It is allowed (and recommended) to use external libraries implementing other well-known algorithms. For example, there is no point in implementing yet another function that calculates MD5 if it is needed for the task - it is perfectly acceptable to use a third-party (or built-in) library;
* The solution should be presented in the form of a link to the public GitHub repository.

> [!IMPORTANT]
> This task was performed using Python Programming Language.

## Expected output

By the end of this task, the following output is expected:

### Before

| mainfolder       | copyfolder      |
|------------------|-----------------|
| continentsfolder | subfolder1      |
| oceansfolder     | subfolder2      |
| planetsfolder    | subfolder3      |
|                  | subfolder4      |
|                  | random8.txt     |
|                  | randomtext1.txt |
|                  | randomtext2.txt |
|                  | randomtext3.txt |
|                  | randomtext4.txt |
|                  | randomtext5.txt |
|                  | randomtext6.txt |
|                  | randomtext7.txt |
|                  | randomtext8.txt |

### After

| mainfolder       | copyfolder       |
|------------------|------------------|
| continentsfolder | continentsfolder |
| oceansfolder     | oceansfolder     |
| planetsfolder    | planetsfolder    |

## How to execute the script?

Once the syncronization must be one-way, the `veeam_task.py` was not executed yet, otherwise, folders and files from **copyfolder** would be erased and replaced, and it would not be possible to test it again. Nevertheless, the program was already tested previously with another files.

To run the program please open the terminal, choose a directory to host the `Veeam_test` directory, and take the following steps:

* Call the used programming language:
  * Example: `$ python` in this case
* Type the relative path to the `veeam_task.py`:
  * Example: "C:\Users\Nelso\PycharmProjects\Veeam_test\veeam_task.py"
* Type the relative path to the `mainfolder`:
  * Example: "C:\Users\Nelso\PycharmProjects\Veeam_test\mainfolder"
* Type the relative path to the `copyfolder`
  * Example: "C:\Users\Nelso\PycharmProjects\Veeam_test\copyfolder"
* Set the time interval (in secs) for the folders' synchronization
  * Example: 15
* Type the relative path to the log file `synchronized.log`
  * Example: "C:\Users\Nelso\PycharmProjects\Veeam_test\synchronized.log" 

Typing all in the same line, the whole combination should be something like this:

`$ python "C:\Users\Nelso\PycharmProjects\Veeam_test\veeam_task.py" "C:\Users\Nelso\PycharmProjects\Veeam_test\mainfolder" "C:\Users\Nelso\PycharmProjects\Veeam_test\copyfolder" 15 "C:\Users\Nelso\PycharmProjects\Veeam_test\synchronized.log"`

> [!NOTE]
> The program is ready to create both the folders and the log file if they do not exist.

## License

© 2022 Veeam Software. Confidential information. All rights reserved. All trademarks are the property of their respective owners.



