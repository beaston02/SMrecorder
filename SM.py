import requests
import json
from websocket import create_connection

UserAgent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Mobile Safari/537.36"
class get:
    def online_models(self):
        r = requests.session()
        online = []
        page = 1
        while True:
            try:
                result = r.get("https://streamate.com/api/search/list?skin_search_kids=0&exact=100&page_number={}&downboost_paid=true".format(
                    page), headers={"User-Agent": UserAgent}).json()
                for model in result['Results']:
                    if model['LiveStatus'] != 'offline':
                        if model['InExclusiveShow'] is False and model['GoldShow'] is False:
                            online.append(model['Nickname'].lower())

                    else:
                        return list(set(online))
                page += 1
            except:
                pass

    def stream(self, model):
        model_info = requests.get("https://streamate.com/ajax/config/?name={}&sakey=&sk=streamate.com&userid=0&version=2.3.1&ajax=1".format(model)).json()
        if model_info['stream']['serverId'] != '0':

            URL = model_info['stream']['nodeHost'] + "/socket.io/?performerid=" + str(
                model_info['performer']['id']) + "&sserver=" + model_info['stream']['serverId'] + "&streamid=" + \
                  model_info['stream'][
                      'streamId'] + "&sakey=&sessiontype=preview&perfdiscountid=0&minduration=0&goldshowid=0&version=7&referrer=hybrid.client.2.3.1%2Favchat.swf&usertype=false&EIO=3&transport=websocket"
            ws = create_connection(URL)
            i = 0
            while i < 5:
                result = ws.recv()
                i = i + 1
                if "roomid" in result:
                    result = json.loads(result[2:])[1]
                    roomInfo = result['data'][22]
                    videourl = ('https:' + requests.utils.quote(
                        '//sea1b-ls.naiadsystems.com/sea1b-hub-api/8101/videourl') + '?' + requests.utils.quote(
                        'payload') + '=' + requests.utils.quote('{"puserid":"' + str(model_info['performer']['id']) + '","roomid":"' + roomInfo[
                            'roomid'] + '","showtype":1,"nginx":1}'))
                    videoinfo = requests.get(videourl).json()
                    videoinfo = requests.get(videoinfo[0]['url']).json()
                    return videoinfo['formats']['mp4-hls']['manifest']
        else: return 'Offline'

    def model_api_check(self, model):
        result = requests.get('https://streamate.com/search.php?q={}&sssjson=1'.format(model),
                              headers={"User-Agent": UserAgent}).json()['Results']
        if model.lower() not in [m['Nickname'].lower() for m in result]:
            return True
        else:
            return False

    def wanted(self, wishlist):
        with open(wishlist) as f:
            models = list(set(f.readlines()))
            wanted = [m.strip('\n').lower() for m in models]
        return (wanted)
