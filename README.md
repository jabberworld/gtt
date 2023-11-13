# Google Translate Transport

A service for Jabber (XMPP) that allows you to create bots that translate sent text via Google Translate.

## Requirements

* python2.7
* python-pyxmpp

## Installation

* Put files of transport into any directory.
* Add service definition into your jabber server config file.

For ejabberd:

Old format:
```
     {5555, ejabberd_service, [
                              {ip, {127.0.0.1}},
                              {access, all},
                              {shaper_rule, fast},
                              {host, "gtrans.domain.com", [{password, "superpassword"}]}
                              ]},
```
New format:
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

Or for Prosody:
```
component_ports = 5555
Component "gtrans.domain.com"
        component_secret = 'superpassword'
```

* Write into config file config.xml all required credentials to connect to Jabber server (transport name, IP, port, password), optionally - set messages limit per day.
* Run somehow gtrans.py - preferably from dedicated user. For example, you can use GNU screen or included gtrans.service for systemd - you can put it into /etc/systemd/system, and write to it required home directory (with a path to service's files), username and group, then run:
```
    # systemctl enable gtrans.service
    # systemctl start  gtrans.service
```

## Usage

Service is creating bots with JIDs like from_lang2to_lang@gtrans.domain.com - for example, en2ru@gtrans.domain.com for translations from english to russian. If you already know JID of reqired bot - just add it into your contact list and authorize.

Also you can add bots via "Registration" from context menu of transport in "Service discovery" - you can choose source language, target language and then bot will be added into contact list.

Additionally, you can see full list of bots in "Service discovery".

After adding, send the text to the bot and it will return a response in the desired language.

If service can't communicate with Google servers - you will get "Translation error"

If you sending messages too often (above limit "tpr" in service's config file) - bot will return "Too fast! Wait a moment..."

If messages count from all users of service is above "tpd" in service's config file - bot will return "Daily limit reached, try later"

Maximum message limit is set to 8 KB.

----

JabberWorld, https://jabberworld.info
