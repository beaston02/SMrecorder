# SMrecorder

This is script to automate the recording of public webcam shows from streamate (and other naiadsystems based sites). 


## Requirements

I have only tested this on debian(7+8) and Mac OS X (10.10.4), but it should run on other OSs

Requires python3.5 or newer. You can grab python3.5.2 from https://www.python.org/downloads/release/python-352/

to install required modules, run:
```
python3.5 -m pip install livesteramer websocket websocket-client requests
```


edit the config.conf file to set the path for the directory to save the videos to, and to set the location of the "wanted.txt" file. You can change the interval between checks also, if you would like.
Add one model per line. The model should match the models name in their chatrooms URL (https://streamate.com/cam/{modelname}/). 
