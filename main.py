from config import bot_key
import threading
import requests
import telebot
import kucoin
import psutil
import time


period = '1day'  # if other period then correct backstep
backstep = 24 * 3600  # seconds in period
pair = 'LTC-USDT'
timeout = 19.125  # secs
amount = '0.001'
coeff = 2.0
long = 20

sell, buy, dead = True, True, True
low, high = 0.0, 0.0
dbg = True


def worker(num_threads):
    bot = telebot.TeleBot(bot_key)
    
    @bot.message_handler(func=lambda m: True)
    def handler(message):
        uid = message.from_user.id
        msg = message.text

        global low, high, sell, buy
        if msg == '/battery':
            s = "??"
            try:
                battery = psutil.sensors_battery()
                t = str(battery)
                k = t.find('percent=')
                if k >= 0 and k + 9 <= t.find(','):
                    s = t[k+8:t.find(',')]
            finally:
                s += '%, '

            ip = '??.??.??.??'
            try:     
                rsp = requests.get('http://httpbin.org/ip')
                ip = rsp.json()['origin']
            finally:
                bot.send_message(uid, 'battery = ' + s + 'low = ' + str(low)+', high = ' + str(high) + ', ip = ' + ip)

        if msg == '/stopboth':
            sell, buy, high, low = False, False, 0.0, 0.0
            bot.send_message(uid, 'Selling and buying is stoped')
        
        if msg == '/stopsell':
            sell, high = False, 0.0
            bot.send_message(uid, 'Selling is stoped')
        
        if msg == '/stopbuy':
            buy, low = False, 0.0
            bot.send_message(uid, 'Buying is stoped')

        if msg == '/both':
            sell, buy = True, True
            bot.send_message(uid, 'Selling and buying is resumed')
        
        if msg == '/sell':
            sell = True
            bot.send_message(uid, 'Selling is resumed')
        
        if msg == '/buy':
            buy = True
            bot.send_message(uid, 'Buying is resumed')

    global dead
    try:
        bot.polling(none_stop=True)
    finally:
        dead = True


"""
ML= SUM (CLOSE, N) / N = SMA (CLOSE, N), где ML — значение средней волны, SUM (…, N) — сумма за отдельное количество 
    периодов, N — периоды, которые учитываются в расчете, SMA — показатель простой скользящей средней.
Верхняя линия представляет собой среднюю волну, которая смещена вверх на D (количество) 
    стандартных отклонений StdDev. Выглядит это так: TL=ML+(D*StdDev).
Нижний график характеризует смещение в другую сторону: BL=ML-(D*StdDev).
Для вычисления значения стандартного отклонения используют формулу: 
    StdDev=SQRT(SUM((CLOSE-SMA(CLOSE, N))^2, N)/N), где SQRT — корень квадратный.
"""


cnt, summ, n = 0, 0, 0
d = {}


def loop():
    global cnt, summ, n, d, long, coeff
    if not sell and not buy:
        cnt = 0
        time.sleep(1)
        exit()

    now = int(time.time()) - backstep
    start = now - (long - 1) * backstep
    
    if cnt == 0:
        r = kucoin.get('market/candles?type=' + period + '&symbol=' + pair +
                       '&startAt=' + str(start) + '&endAt=' + str(now))

        if r.status_code != 200:
            print('bad candles at', time.ctime())
            cnt = 0
            exit()

        d = r.json()['data']
        n = 1 + len(d)
        summ = 0
        for p in d:
            summ += float(p[2])
    cnt = (cnt + 1) & 0xf

    r = kucoin.get('market/orderbook/level1?symbol=' + pair)
    if r.status_code != 200:
        print('bad price at', time.ctime())
        exit()

    price = float(r.json()['data']['price'])
    ml = (summ + price) / n
    sq = 0

    for p in d:
        sq += (float(p[2]) - ml)**2
    sq = ((sq + (price-ml)**2) / n)**0.5

    global low, high
    if sell:
        high = round(ml + sq * coeff, 4)
    if buy:
        low = round(ml - sq * coeff, 4)
    if dbg:
        print(time.ctime(), low, high, end='\r', flush=True)

    if (price < ml + sq * coeff) and (price > ml - sq * coeff):
        time.sleep(timeout)
        cnt = 0
        exit()

    p = pair
    if sell and (price > high):
        jsn = '{"clientOid":"'+p+'-SELL","symbol":"'+p+'","side":"sell","size":"'+amount+'","price":"'+str(price)+'"}'
        if dbg:
            print('\n', jsn, '\n', kucoin.post('orders', jsn).content)

    elif buy and (price < low):
        jsn = '{"clientOid":"'+p+'-BUY","symbol":"'+p+'","side":"buy","size":"'+amount+'","price":"'+str(price)+'"}'
        if dbg:
            print('\n', jsn, '\n', kucoin.post('orders', jsn).content)


if __name__ == '__main__':

    print('Started at', time.ctime())
    thread = threading.Thread(target=worker, args=(1,))
    thread.start()
    dead = False

    while True:

        if dead:
            print('\n telebot deaded at', time.ctime())
            try:
                thread = threading.Thread(target=worker, args=(1,))
                thread.start()
                dead = False
            finally:
                continue
    
        try: 
            loop()
        finally:
            continue
