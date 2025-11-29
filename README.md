# OCM Trim Cleaner
When using media management in Davinci Resolve it renames your files. This undoes that renaming without overwriting files.

## How to use
1. Run Davinci Resolve's Media Management to an empty directory
2. Open terminal and type this command `python ./ocm_trim_cleaner.py /path/to/media`
It's that easy!

## What it does
- Find any directory ending in _S###, remove that extension, and consolidate media in those directories.
- Find files ending in _S###.***, creates a folder for each _S### and puts media in there. Then it renames it to its original name

### Before running the script
```
/example_directory
│
├── file_S001.mov
├── file_S002.mov
├── anotherfile_S001.mov
├── dir_S001
    └── subfile.01.dpx
└── dir_S002
    └── subfile.02.dpx
```
### After running the script
```
/example_directory
│
├── S001
    ├── file.mov
    └── anotherfile.mov
├── S002
    └── file.mov
├── 
└── dir
    ├── subfile.01.dpx
    └── subfile.02.dpx
