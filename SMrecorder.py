import time, threading, datetime, os, sys, configparser
import SM
from livestreamer import Livestreamer
from subprocess import call
from queue import Queue

get = SM.get()

Config = configparser.ConfigParser()
Config.read(sys.path[0] + "/config.conf")
settings = {
        'save_directory' : Config.get('paths', 'save_directory'),
        'wishlist' : Config.get('paths', 'wishlist'),
        'interval' : int(Config.get('settings', 'checkInterval')),
        'post_processing_command': Config.get('settings', 'post_processing_command'),
        'post_processing_threads': int(Config.get('settings', 'post_processing_threads')),
}
nonApiModels = []
if not os.path.exists("{path}".format(path=settings['save_directory'])):
    os.makedirs("{path}".format(path=settings['save_directory']))
recording = []
def getOnlineModels():
    global nonApiModels
    wanted = get.wanted(settings['wishlist'])
    nonApiModels = list(set(nonApiModels) - set(wanted))
    for model in get.onlineModels():
        if model.lower() not in recording and model.lower() in wanted:
            thread = threading.Thread(target=startRecording, args=(model,))
            thread.start()
    for model in [m for m in nonApiModels if m not in recording]:
        if get.stream(model) is not 'Offline':
            thread = threading.Thread(target=startRecording, args=(model,))
            thread.start()

def startRecording(model):
    try:
        recording.append(model.lower())
        session = Livestreamer()
        url = get.stream(model)
        if url == 'Offline':
            recording.remove(model.lower())
            return
        streams = session.streams("hlsvariant://" + url)
        stream = streams["best"]
        fd = stream.open()
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime("%Y.%m.%d_%H.%M.%S")
        file_path = "{path}/{model}/{st}_{model}.mp4".format(path=settings['save_directory'], model=model,st=st)
        directory = file_path.rsplit('/', 1)[0] + '/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(file_path, 'wb') as f:
            while True:
                try:
                    data = fd.read(1024)
                    f.write(data)
                except:
                    break

    finally:
        recording.remove(model.lower())
        if settings['post_processing_command'] and file_path:
            processing_queue.put({'model': model, 'path': file_path})

def findNonApiModels():
    while True:
        wanted = get.wanted(settings['wishlist'])
        for model in set(wanted) - set(nonApiModels):
            if get.modelApiCheck(model):
                nonApiModels.append(model)
        time.sleep(21600)
def postprocess():
    while True:
        while processing_queue.empty():
            time.sleep(1)
        parameters = processing_queue.get()
        model = parameters['model']
        path = parameters['path']
        filename = path.rsplit('/', 1)[1]
        directory = path.rsplit('/', 1)[0] + '/'
        file = os.path.splitext(filename)[0]
        call(settings['post_processing_command'].split() + [path, filename, directory, model, file, 'streamate'])

if __name__ == '__main__':
    if settings['post_processing_command']:
        processing_queue = Queue()
        postprocessing_workers = []
        for i in range(0, settings['post_processing_threads']):
            t = threading.Thread(target=postprocess)
            postprocessing_workers.append(t)
            t.start()
    t = threading.Thread(target=findNonApiModels)
    t.start()
    while True:
        getOnlineModels()
        for i in range(settings['interval'], 0, -1):
            sys.stdout.write("\033[K")
            print("{} model(s) are being recorded. Next check in {} seconds".format(len(recording), i))
            sys.stdout.write("\033[K")
            print("the following models are being recorded: {}".format(recording), end="\r")
            time.sleep(1)
            sys.stdout.write("\033[F")
