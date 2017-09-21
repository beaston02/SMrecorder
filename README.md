# SMrecorder

This script automates the recording of public webcam shows from streamate (and other naiadsystems based sites). 


## Requirements

I have only tested this on debian(7+8) and Mac OS X (10.10.4), but it should run on other OSs

Requires python3.5 or newer. You can grab python3.5.2 from https://www.python.org/downloads/release/python-352/

to install required modules, run:
```
python3.5 -m pip install livestreamer websocket websocket-client requests
```


edit the config.conf file to set the path for the directory to save the videos to, and to set the location of the "wanted.txt" file. You can change the interval between checks also, if you would like.
Add one model per line. The model should match the models name in their chatrooms URL (https://streamate.com/cam/{modelname}/). 


## Configuration

edit the config.conf file to set the path for the directory to save the videos to, and to set the location of the "wanted.txt" file. You can change the interval between checks also, if you would like.

You can set a script to run after the recording has finished. Just set the command to be ran in the "post_processing_thread" option and the number of threads. 

the arguments passed to the script are:

1 = path - the full path to the file
2 = filename - the filename only (including extension)
3 = directory - the directory path
4 = model - the models username
5 = file - the filename less the extension
6 = streamate - thats it, simply returns "streamate"
