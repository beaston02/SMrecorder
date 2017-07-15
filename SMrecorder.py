import urllib.request, json, time, requests, threading, datetime, os, sys, configparser
from websocket import create_connection
from livestreamer import Livestreamer

Config = configparser.ConfigParser()
Config.read(sys.path[0] + "/config.conf")
save_directory = Config.get('paths', 'save_directory')
wishlist = Config.get('paths', 'wishlist')
interval = int(Config.get('settings', 'checkInterval'))

if not os.path.exists("{path}".format(path=save_directory)):
    os.makedirs("{path}".format(path=save_directory))
recording = []
UserAgent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Mobile Safari/537.36"
cookie = ""
def getOnlineModels():
    global cookie
    online = []
    wanted = []
    with open(wishlist) as f:
        for model in f:
            models = model.split()
            for theModel in models:
                wanted.append(theModel.lower())
    f.close()
    if cookie == "":
        r = requests.get('http://streamate.com', headers={
            "User-Agent": UserAgent})
        cookie = r.headers['Set-Cookie']
    offline = False
    page = 1
    while offline == False:
        req = urllib.request.Request("https://api.naiadsystems.com/search/V1/list?skin_search_kids=0&exact=1&page_number={}&results_per_page=500&sort_order=default".format(page))
        req.add_header("User-Agent", UserAgent)
        req.add_header('connection', 'keep-alive')
        req.add_header('cookie', cookie)
        req.add_header('Host', 'streamate.com')
        req.add_header('Referer', 'https://streamate.com/?')
        resp = urllib.request.urlopen(req)
        result = resp.read()
        result = json.loads(result.decode())
        for model in result['Results']:
            if model['LiveStatus'] != 'offline':
                if model['InExclusiveShow'] is False and model['GoldShow'] is False:
                    online.append(model['Nickname'].lower())
                    if model['Nickname'].lower() not in recording and model['Nickname'].lower() in wanted:
                        model = model['Nickname']
                        thread = threading.Thread(target=startRecording, args=(model,))
                        thread.start()
            else:
                offline = True
                break
        page = page + 1

def startRecording(model):
    try:
        recording.append(model.lower())
        req = urllib.request.Request(
            "https://streamate.com/ajax/config/?name={}&sakey=&sk=streamate.com&userid=0&version=2.3.1&ajax=1".format(
                model))
        resp = urllib.request.urlopen(req)
        modelinfo = resp.read()
        modelinfo = json.loads(modelinfo.decode())

        if modelinfo['stream']['serverId'] != '0':

            URL = modelinfo['stream']['nodeHost'] + "/socket.io/?performerid=" + str(
                modelinfo['performer']['id']) + "&sserver=" + modelinfo['stream']['serverId'] + "&streamid=" + \
                  modelinfo['stream'][
                      'streamId'] + "&sakey=&sessiontype=preview&perfdiscountid=0&minduration=0&goldshowid=0&version=7&referrer=hybrid.client.2.3.1%2Favchat.swf&usertype=false&EIO=3&transport=websocket"
            ws = create_connection(URL)
            i = 0
            while i < 5:
                result = ws.recv()
                i = i + 1
                if "roomid" in result:
                    result = json.loads(result[2:])[1]
                    roomInfo = result['data'][22]
                    videourl = ('https:' + urllib.request.quote(
                        '//sea1b-ls.naiadsystems.com/sea1b-hub-api/8101/videourl') + '?' + urllib.request.quote(
                        'payload') + '=' + urllib.request.quote(
                        '{"puserid":"' + str(modelinfo['performer']['id']) + '","roomid":"' + roomInfo[
                            'roomid'] + '","showtype":1,"nginx":1}'))
                    videoinfo = urllib.request.urlopen(videourl)
                    videoinfo = videoinfo.read().decode('utf-8')
                    videoinfo = json.loads(videoinfo)
                    videoinfo = urllib.request.urlopen(videoinfo[0]['url'])
                    videoinfo = videoinfo.read().decode('utf-8')
                    videoinfo = json.loads(videoinfo)
                    session = Livestreamer()
                    streams = session.streams("hlsvariant://" + videoinfo['formats']['mp4-hls']['manifest'])
                    stream = streams["best"]
                    fd = stream.open()
                    ts = time.time()
                    st = datetime.datetime.fromtimestamp(ts).strftime("%Y.%m.%d_%H.%M.%S")
                    if not os.path.exists("{path}/{model}".format(path=save_directory, model=model)):
                        os.makedirs("{path}/{model}".format(path=save_directory, model=model))
                    with open("{path}/{model}/{st}_{model}.mp4".format(path=save_directory, model=model,
                                                                       st=st), 'wb') as f:
                        while True:
                            try:
                                data = fd.read(1024)
                                f.write(data)
                            except:
                                recording.remove(model.lower())
                                f.close()
                                return ()

    except:
        recording.remove(model.lower())



if __name__ == '__main__':
    while True:
        getOnlineModels()
        for i in range(interval, 0, -1):
            sys.stdout.write("\033[K")
            print("{} model(s) are being recorded. Next check in {} seconds".format(len(recording), i))
            sys.stdout.write("\033[K")
            print("the following models are being recorded: {}".format(recording), end="\r")
            time.sleep(1)
            sys.stdout.write("\033[F")
