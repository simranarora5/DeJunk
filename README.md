# deJunk
A desktop application that effectively detects duplicate photos on your computer, removes them, and frees up disc space...

Steps to convert this code to an executable file:
1. Install the PyInstaller Package for windows(auto-py for MAC).
2. Run pyInstaller command in terminal for main.py file.
3. It will generate a folder named 'dist' and there you will find main.exe file.
4. Run main.exe 

Pre-requisites:
1. Python and MongoDB installed on system.
2. All images must be a root folder. Sub-directories are not supported in current version.

Features:
1. The application facilitates detection and deletion of duplicate images and retrieval of deleted images as well.
2. The deleted images are stored in MongoDB.
3. Deleted images can be retrieved based on folder name.  
4. Machine learning model has been built to detect deleted images with 90% of accuracy.







