from hashlib import sha256
from config import kusecret, kukey, pswphrase
import requests
import base64
import time
import hmac


urlku = 'https://api.kucoin.com/api/v1/'


def get(service, data=''):
    now = int(time.time() * 1000)
    str_to_sign = str(now) + 'GET' + '/api/v1/'+service+data
    signature = base64.b64encode(hmac.new(kusecret.encode('utf-8'), str_to_sign.encode('utf-8'), sha256).digest())
    passphrase = base64.b64encode(hmac.new(kusecret.encode('utf-8'), pswphrase.encode('utf-8'), sha256).digest())
    headers = {
                "KC-API-SIGN": signature,
                "KC-API-TIMESTAMP": str(now),
                "KC-API-KEY": kukey,
                "KC-API-PASSPHRASE": passphrase,
                "KC-API-KEY-VERSION": "2"
               }
    return requests.get(urlku+service, headers=headers, data=data)


def post(service, data=''):
    now = int(time.time() * 1000)
    str_to_sign = str(now) + 'POST' + '/api/v1/' + service + data
    signature = base64.b64encode(hmac.new(kusecret.encode('utf-8'), str_to_sign.encode('utf-8'), sha256).digest())
    passphrase = base64.b64encode(hmac.new(kusecret.encode('utf-8'), pswphrase.encode('utf-8'), sha256).digest())
    headers = {
                "KC-API-SIGN": signature,
                "KC-API-TIMESTAMP": str(now),
                "KC-API-KEY": kukey,
                "KC-API-PASSPHRASE": passphrase,
                "KC-API-KEY-VERSION": "2",
                "Content-Type": "application/json"
              }

    return requests.post(urlku + service, headers=headers, data=data)
