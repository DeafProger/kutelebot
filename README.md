# kutelebot

При создании торгового робота, работающего в одном из 4 режимов:

- только покупки
- только продажи
- в режиме покупки/продажи
- в режиме бездействия

было выработано решение:
Приложение работает в двухпоточном режиме (GIL учитывается).
В одном потоке работает телеграм-бот, в котором можно задавать режим работы торгового робота.
В другом потоке работает сам торговый робот, а также с помощью флага dead отслеживается, что телеграм-бот жив. В случае выпадения телеграм-бота он заново перезапускается.  

![image](https://github.com/user-attachments/assets/3eb6f975-f047-41b6-a9b0-6515bd063128)


