# What is Studio Doing?

This is a simple script which displays and optionally kills processes which are executing out of folders and subtrees associated with Simplicity Studio.  The operating system is used to set the default base locations, these are:
### Darwin / MacOS
* `${HOME}/.silabs`
* `/Applications/SimplicityInstaller.app`
### Linux
* `${HOME}/.silabs`
* `/opt/SimplicityInstaller`
### Windows
* `${HOME}/.silabs`

## Example Usage
Simplicity Studio is running.  Somehow everything seems to be running slowly.
```
$ wpython wisd.py 
sdm-service.exe (47960)
studio.exe (9752)
    sts_back_end.exe (36932)
        hw-db-service.exe (42708)
    chromium.exe (46092)
        chromium.exe (5216)
        chromium.exe (10676)
        chromium.exe (23924)
        chromium.exe (39796)
        chromium.exe (40936)
        chromium.exe (41380)
```
You close Studio.  After a while you are suspicious...
```
$ wpython wisd.py 
sdm-service.exe (47960)
sts_back_end.exe (36932)
    hw-db-service.exe (42708)
```
After a few hours, they are still running.  This is where the `--kill` switch becomes interesting.
```
$ wpython wisd.py -k
sdm-service.exe (47960)
sts_back_end.exe (36932)
    hw-db-service.exe (42708)
No processes left
```
The logic here is that the processes are recorded, then sent kill signals, then displayed.  After display, the sequence is iterated again.  Potentially termination may not be immediate, so displaying gives a slight delay.  This should also take case of cases where new process are spawned to replace terminated processes.  I have observed on all platforms that a single iteration has always been sufficient.

## Current options
```
$ wpython wisd.py -h
$ wpython wisd.py -h
usage: wisd.py [-h] [-k] [--cwd] [-v] [--replace REPLACE] [--add ADD]

List and optionally kill processes

options:
  -h, --help         show this help message and exit
  -k, --kill
  --cwd
  -v, --verbose
  --replace REPLACE  replace default base folders with comma delimited list     
  --add ADD          supplement default base folders with comma delimited list  

Default behavior is to list processes. Kill mode loops until no processes are   
left.
```
