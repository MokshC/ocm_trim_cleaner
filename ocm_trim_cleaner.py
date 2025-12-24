# Moksh Chitkara
# OCM Trim Cleaner v1.0.4
# Last Updated: Dec 23th 2025

import os
import sys
import re
import shutil
from pathlib import Path
import threading

# get input from user with optional verbose flag
def ask_user():
    args = sys.argv
    
    if len(args) >= 2:                              # if theres multiple args
        verbose = False                             
        for arg in args[1:]:                        # check for -v flag
            if arg in ("-v", "--verbose"):
                verbose = True
            elif arg in ("-h", "--help"):           # or -h flag
                raise ValueError("Usage: ocm-trim-renamer <directory_path> [-v|--verbose]")
            else:                                   # and set the path
                path = Path(arg)
    else:                                           # otherwise give a hint on how to use it
        raise ValueError("Usage: ocm-trim-renamer <directory_path> [-v|--verbose]")

    if path.exists() and path.is_dir():             # if the path exists continue, else error
        return path, verbose
    else:
        raise ValueError(f"The directory '{path}' does not exist or is not a directory.")

# finishes multi threading tasks
def thread_finish(t, threads):
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
# checks file name for pattern
# input: s [string]
# output: bool
def name_check(s, verbose):

    file_pattern = r'_S\d{3}\.\w{3}$'   # file pattern
    dir_pattern = r'_S\d{3}$'           # directory pattern
    return bool((re.search(file_pattern, s)) or (re.search(dir_pattern, s)))

# Creates list of files and dirs that need to be moved and renamed
# input: path
# output: tasks [list]
def task_out(path, verbose):

    try:                                                            # get the path with error check
        entries = os.listdir(path)
    except:
        print(f"Failed to read the directory: {path}")

    tasks = []                                                      # for each entry
    for entry in entries:
        file_path = path / entry   
        if name_check(file_path.name, verbose):                     # check if we need it
            tasks.append(file_path)                                 # and append to tasks
            
    if verbose:
        l = len(tasks)
        print(f"There are {l} tasks that need to be run.")
            
    return tasks

# just shutil move but for threads
def move(item, new_dir, verbose):
    path = new_dir / item.name
    if os.path.exists(path):
        raise ValueError(f"Trying to move The file '{item}' but '{path}' already exists. New dir: {new_dir}")    
    else:
        shutil.move(str(item), str(path))
        if verbose:
            print(f"Moved {item} -> {path}")
        return path

# Returns True if len iterable greater than 1
# input: iterable
# output: Bool
def iter_over_one(i):
    count = 0
    try:
        for e in i:
            count += 1
            if count > 1:
                return True
    except:
        raise ValueError(f"The iterable has length 0.")
    return False

# Given a path it is moved and renamed
# input: path
# output: none
def cleanup(path, verbose):

    print("ITER DER", path, iter_over_one(path.iterdir()))

    # If it is an image sequence
    if path.is_dir() and not str(path).endswith(".RDC"):
        new_dir_name = re.sub(r'_S\d{3}$', '', path.name)   # get new name
        new_dir = path.parent / new_dir_name                # create new directory path
        os.makedirs(new_dir, exist_ok=True)                 # create directory on system
        
        
        # move everything using multithreading
        threads = []
        for item in path.iterdir():                         
            t = threading.Thread(target=move, args=(item, new_dir))
            threads.append(t)
        thread_finish(t, threads)
    
        path.rmdir()                                        # delete old directory

        return 

    matches = re.findall(r'_S\d+', path.name)           # get _S### out of name
    new_dir = path.parent / matches[-1][1:]             # create new directory path titled S###
    os.makedirs(new_dir, exist_ok=True)                 # create directory on system
    
    # If it is a R3D file
    if path.is_dir() and str(path).endswith(".RDC"):
        new_dir = new_dir / (re.sub(r'_S\d{3}', '', path.name))     # recreate og subdirectory without _S###
        os.makedirs(new_dir, exist_ok=True)                         # create subdirectory on system
        
        if (iter_over_one(path.iterdir())):
            # move everything using multithreading
            threads = []
            for item in path.iterdir():                         
                t = threading.Thread(target=move, args=(item, new_dir))
                threads.append(t)
            thread_finish(t, threads)
        else:
            move(next(path.iterdir()), new_dir, verbose)            # move the file
        
        path.rmdir()                                                # delete old directory

    
    # if it is a video file
    else:
        moved_path = move(path, new_dir, verbose)               # move the item
        
        new_file_name = re.sub(r'_S\d{3}', '', moved_path.name) # rename it removing S###
        renamed_path = moved_path.parent / new_file_name        # create path
        moved_path.rename(renamed_path)                         # do the rename on system

if __name__ == "__main__":
    path, verbose = ask_user()  # get path and verbose preference

    tasks = task_out(path, verbose)
    
    if len(tasks) > 0:
        threads = []
        for task in tasks:
            t = threading.Thread(target=cleanup, args=(task, verbose))
            threads.append(t)
        thread_finish(t, threads)
        
        if verbose:
            print(f"Ran {len(tasks)} tasks!")
        
    print("Done!")
