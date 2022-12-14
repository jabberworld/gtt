# Google Translate Transport

Сервис для Jabber (XMPP), позволяющий создавать ботов, переводящих отправленный текст через Google Translate.

## Требования

* python2.7
* python-pyxmpp

## Установка

* Разместить файлы транспорта в любом удобном каталоге.
* Добавить в конфиг-файл Jabber-сервера описание транспорта. На примере ejabberd:

Старый формат:
```
     {5555, ejabberd_service, [
                              {ip, {127.0.0.1}},
                              {access, all},
                              {shaper_rule, fast},
                              {host, "gtrans.domain.com", [{password, "superpassword"}]}
                              ]},
```
 Новый формат:
```
    -
      port: 5555
      ip: "127.0.0.1"
      module: ejabberd_service
      access: all
      hosts:
       "gtrans.domain.com":
         password: "superpassword"
      shaper_rule: fast
```

* В файле config.xml транспорта прописать используемые параметры подключения к Jabber-серверу (название транспорта, IP, порт, пароль), опционально - установить лимиты на число сообщений в сутки.
* Тем или иным способом запустить gtrans.py (в идеале от отдельного пользователя) - можно в GNU screen или с помощью идущего в комплекте gtrans.service-файла для systemd. Последний можно разместить в ~/.config/systemd/user/gtrans.service, далее выполнить:
```
    systemctl --user enable gtrans.service
    systemctl --user start gtrans.service
```
* Для автостарта пользовательского service-файла использовать команду:
```
    # loginctl enable-linger username
```
* ...либо все то же самое, но глобально, разместив service-файл в /etc/systemd/system, а в gtrans.service указать нужные имя и группу пользователя.

## Использование

Транспорт создает ботов с JID'ами вида с_языка2на_язык@gtrans.domain.com - например, en2ru@gtrans.domain.com для перевода с английского на русский. Если вы уже знаете JID нужного вам бота - можно просто добавить его в список контактов и авторизовать.

Также доступна функция добавления бота через пункт "Регистрация" в браузере сервисов - там можно выбрать исходный язык, язык назначения, после чего нужный контакт будет добавлен.

Плюс полный список (с возможностью добавления контакта) доступен в браузере сервисов напрямую.

После добавления отправьте боту текст и он вернет ответ на нужном языке.

Если есть проблема с коммуникацией с серверами гугла - он вернет "Translation error"

Если сообщения шлются сильно часто (чаще установленного в конфиг-файле параметра tpr) - бот вернет "Too fast! Wait a moment..."

Если число сообщений от всех пользователей превышает установленный в конфиг-файле лимит tpd - бот вернет "Daily limit reached, try later"

Лимит на размер сообщения установлен в 8 КБ.

----

JabberWorld, https://jabberworld.info
