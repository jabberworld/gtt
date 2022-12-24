#!/usr/bin/python -u
# -*- coding: UTF8 -*-
#
# GTT           Python based Google Translate Transport.
#               2022 rain from JabberWorld. JID: rain@jabberworld.info
# Licence:      GPL v3
# Requirements:
#               python-pyxmpp - https://github.com/Jajcus/pyxmpp

import os
import sys
import time
import xml.dom.minidom
import re
from json import loads
import urllib2

from pyxmpp.jid import JID
from pyxmpp.presence import Presence
from pyxmpp.message import Message

from pyxmpp.jabber.disco import DiscoItem
from pyxmpp.jabber.disco import DiscoItems

import pyxmpp.jabberd.all

programmVersion="1.1"

config=os.path.abspath(os.path.dirname(sys.argv[0]))+'/config.xml'

dom = xml.dom.minidom.parse(config)

NAME =  dom.getElementsByTagName("name")[0].childNodes[0].data
HOST =  dom.getElementsByTagName("host")[0].childNodes[0].data
PORT =  dom.getElementsByTagName("port")[0].childNodes[0].data
PASSWORD = dom.getElementsByTagName("password")[0].childNodes[0].data

# Throttle limits
TPR =  dom.getElementsByTagName("tpr")[0].childNodes[0].data
TPD =  dom.getElementsByTagName("tpd")[0].childNodes[0].data

class Component(pyxmpp.jabberd.Component):
    start_time = int(time.time())
    msgstat = {} # list of requests per JID
    lastmsg = start_time # last request marker
    name = NAME
    tpr = int(TPR) # throttle by request per second
    tpd = int(TPD) # throttle by request per day
    gttlogo = 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAFdklEQVR42r2XBWwbWRCGW7FOzMdiDnl3YwxdfWGqw1ymJKKSoMzMzMzc4zIzM3MTwzHu2l7/Nx51Tz6ZtilY+sye+Xf+ee+NO4mi+JFgSJ4sGJLO0+MV4rIOrgiC4Qj9NpHo9EY3CrTGlFniz6qfhi+6zdNH02wYM4tBQgaLgkAxhI4LEEXp7+zmrXDM9sMxy6sTH7IaZgQF7KMKfEC8gYBUE/IGHeKgjpn/EHIc/mEReUOOQzLaPIIhRaDbmwo4+EqArJuSSS6Ys+sgpCQOCgrgKrw3AYxCNkwL2nAiOTm5ICkpKUcnuYTdYDB8bjKZOndQgGbDMbLBGsjKylLy8vKU3NxcXdjtdlmSpOtUOUdUAV1nyCid8Q9Kpv8Hv+5KhNpgstdgwvhxuHLlCi5duqSLc+fOYejQoaAq3IsogJJwsp5LZEzZ68WKwz7M+taLASv4M0azIb12Cvr26YWnT5+ivb1dF263G7t27YLRaAyECdASTNrjxSOXCuevAdxrV/HiZxVtPwew9KAXFbP5e2xD7uCj6JKdh5MnT8DpdKKtrS0e/L09e/aAegBhAkqp1MO3KnD/FsA3l/0YsFJB7TwZvZbKWHvMh0uPVfRYzPZwBUomOmG2V2PRwgUc+OXLlx0WwFdVSVd35r4fJ+76UTVHZu+Lp/2DIiL4vG6+HNYL6TWT0YdsePLkCScgEWGPegRw4D7LZLz8WWXvKTGLmPa1F8sO+bj8QeZ+70XTwhAbBh2BnWw4deokXC4XJ7h8+TKmTJmCO3fu8GvN/1gCuPzNKxX2fdR2hQU0UqLjd/x44FS5F556VPytBDBim8IVCbVhzuxZuHXrFm7evIlt27YhOzsbP/zwA7++fv06c//+/dgWNCyQcZ+SrT/howRcalTPlbn0wcc533nhov5oXa2wYM2GzLopyEi3obS0lKF9AWazGQUFBSgpKUFRUREzcuRItiSKAPYXa6jZ2n8JcDMGXxe/8r9llYK7bSr2X/ejfNYrCwjelAYdhjUtk6owGzt37sT27duZzZs3o6KiAvX19diyZQuOHj0acxVw0Hq62kM3/bwSvqWVsOSAFzvO+vDiJxVXn6rot1xbBTIYtqGdbVi8aCEtyZN4/PgxfvzxRxw5cgS0+7EYj8fDfRBLAMHBeekt2OfFxUcqHrpUXHumYu1xX8gSlMPIqJmI2ppqVFZWYurUqXj06BFaW1vRr18/fh57FYRtxVx2XpZUEV4N5Hnk5NpqGHgI2TkFmDBhAvLz8zFo0CB+3Ldvn7ZH6BWgiWAhIcQ4oNiGNrKhCksWL8LYsWORmJjITfc6O+Ebk149AU2N9ejVqxdsNhvq6upw4cIF/RXoMGyDj2MJkgkV5eXYu3cvunfvzmJu3LjBDUgiIgk49OYCNBsmtMGYVY5ZM2dw1585c4aXYUtLC29S4RWQTIHcgQfgmK1ygDfHSzaMR/OA/nxEUzJe+1VVVVi3bh2//p8AQTDcy6gcgaJRd1E89tGbM+4J7P024svsXLr609DOgGvXruHu3bvhFQiORTSaX0+1ZcvG9HzlNVGN6QUwZhSFUIxUWw6k1FQ+D7QZQTuIIvVAZ6rC50JKkp0m3FwiRyfZgiFpm2QtgqlkDkylC4iFMOaPgkG0YgBZQIdQ/HmgIzdtDBeEZIdo6qJYKrfA2nAElqodEGxV6NmzJ65evap1/RsKiCGC+ISE3DIVToSlejeEtBo01Ieve40wC95cgET2pSyW0qsgZTSipqYG586d5aGTkkSDh5ZVq1ZBkqS/3+A/pahVwSGIokLB0NzcjOnTp/NBFItx48ahsLDQT2P5Gg72ZlUQP6LH3SToKgW8TP+S4nGFOJ+SkjKJfvPRvxq8CCnBwq3aAAAAAElFTkSuQmCC'

    LANGUAGES = {
    'af': 'afrikaans',
    'sq': 'albanian',
    'am': 'amharic',
    'ar': 'arabic',
    'hy': 'armenian',
    'az': 'azerbaijani',
    'eu': 'basque',
    'be': 'belarusian',
    'bn': 'bengali',
    'bs': 'bosnian',
    'bg': 'bulgarian',
    'ca': 'catalan',
    'ceb': 'cebuano',
    'ny': 'chichewa',
    'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)',
    'co': 'corsican',
    'hr': 'croatian',
    'cs': 'czech',
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    'eo': 'esperanto',
    'et': 'estonian',
    'tl': 'filipino',
    'fi': 'finnish',
    'fr': 'french',
    'fy': 'frisian',
    'gl': 'galician',
    'ka': 'georgian',
    'de': 'german',
    'el': 'greek',
    'gu': 'gujarati',
    'ht': 'haitian creole',
    'ha': 'hausa',
    'haw': 'hawaiian',
    'iw': 'hebrew',
    'he': 'hebrew',
    'hi': 'hindi',
    'hmn': 'hmong',
    'hu': 'hungarian',
    'is': 'icelandic',
    'ig': 'igbo',
    'id': 'indonesian',
    'ga': 'irish',
    'it': 'italian',
    'ja': 'japanese',
    'jw': 'javanese',
    'kn': 'kannada',
    'kk': 'kazakh',
    'km': 'khmer',
    'ko': 'korean',
    'ku': 'kurdish (kurmanji)',
    'ky': 'kyrgyz',
    'lo': 'lao',
    'la': 'latin',
    'lv': 'latvian',
    'lt': 'lithuanian',
    'lb': 'luxembourgish',
    'mk': 'macedonian',
    'mg': 'malagasy',
    'ms': 'malay',
    'ml': 'malayalam',
    'mt': 'maltese',
    'mi': 'maori',
    'mr': 'marathi',
    'mn': 'mongolian',
    'my': 'myanmar (burmese)',
    'ne': 'nepali',
    'no': 'norwegian',
    'or': 'odia',
    'ps': 'pashto',
    'fa': 'persian',
    'pl': 'polish',
    'pt': 'portuguese',
    'pa': 'punjabi',
    'ro': 'romanian',
    'ru': 'russian',
    'sm': 'samoan',
    'gd': 'scots gaelic',
    'sr': 'serbian',
    'st': 'sesotho',
    'sn': 'shona',
    'sd': 'sindhi',
    'si': 'sinhala',
    'sk': 'slovak',
    'sl': 'slovenian',
    'so': 'somali',
    'es': 'spanish',
    'su': 'sundanese',
    'sw': 'swahili',
    'sv': 'swedish',
    'tg': 'tajik',
    'ta': 'tamil',
    'te': 'telugu',
    'th': 'thai',
    'tr': 'turkish',
    'uk': 'ukrainian',
    'ur': 'urdu',
    'ug': 'uyghur',
    'uz': 'uzbek',
    'vi': 'vietnamese',
    'cy': 'welsh',
    'xh': 'xhosa',
    'yi': 'yiddish',
    'yo': 'yoruba',
    'zu': 'zulu',
}

    def trans(self, fr, to, text):
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&dt=t&sl=" +fr+ "&tl=" +to+ "&q=" + urllib2.quote(text.encode("utf-8"))
        req = urllib2.Request(url)
        try:
            site = urllib2.urlopen(req, timeout = 10)
            site = site.read()
            if not site:
                return "Translation error"
            else:
                translated = loads(site)
                translated_text = ''
                for i in translated[0]:
                    translated_text += i[0]
                print("Got answer: " + translated_text.encode("utf-8"))
                return translated_text
        except:
            return "Translation error"

    def checklang(self, node):
        regcheck = "(" + "|".join(self.LANGUAGES) + "|auto)2(" + "|".join(self.LANGUAGES) + ")"
        if re.match(regcheck, node):
            return True
        return False

    def authenticated(self):
        pyxmpp.jabberd.Component.authenticated(self)
        self.disco_info.add_feature("http://jabber.org/protocol/disco#info")
        self.disco_info.add_feature("http://jabber.org/protocol/disco#items")
        self.disco_info.add_feature("http://jabber.org/protocol/stats") # XEP-0039
        self.disco_info.add_feature("jabber:iq:version")
        self.disco_info.add_feature("jabber:iq:register")
        self.disco_info.add_feature("jabber:iq:last")
        self.disco_info.add_feature("urn:xmpp:ping")
        self.disco_info.add_feature("urn:xmpp:time")
        self.disco_info.add_feature("vcard-temp")
        self.stream.set_iq_get_handler("vCard","vcard-temp",self.get_vCard)
        self.stream.set_iq_get_handler("query","jabber:iq:version",self.get_version)
        self.stream.set_iq_get_handler("query","jabber:iq:last",self.get_last)
        self.stream.set_iq_get_handler("ping","urn:xmpp:ping",self.pingpong)
        self.stream.set_iq_get_handler("time","urn:xmpp:time",self.get_time)
        self.stream.set_iq_get_handler("query","jabber:iq:register",self.get_register)
        self.stream.set_iq_set_handler("query","jabber:iq:register",self.set_register)
        self.stream.set_iq_get_handler("query", "http://jabber.org/protocol/stats", self.get_stats)
        self.stream.set_presence_handler("available",self.presence)
        self.stream.set_presence_handler("unavailable",self.presence)
        self.stream.set_presence_handler("subscribe",self.presence_control)
        self.stream.set_presence_handler("subscribed",self.presence_control)
        self.stream.set_presence_handler("unsubscribe",self.presence_control)
        self.stream.set_presence_handler("unsubscribed",self.presence_control)
        self.stream.set_message_handler("normal", self.message)

    def get_stats(self, iq):
# It's incorrect implementation of XEP-0039, it should be in 2 steps (like search)
        iq = iq.make_result_response()
        q = iq.new_query("http://jabber.org/protocol/stats")

        upt = q.newChild(None, "stat", None)
        upt.setProp("name", 'time/uptime')
        upt.setProp("units", 'seconds')
        upt.setProp("value", str(int(time.time()) - self.start_time))

        ts = time.time()
        hourly = daily = users = 0
        for i in self.msgstat:
            users += 1
            for j in self.msgstat[i]:
                if j > ts - 86400:
                    daily += 1
                    if j > ts - 3600:
                        hourly += 1

        reqsh = q.newChild(None, "stat", None)
        reqsh.setProp("name", 'messages/hourly')
        reqsh.setProp("units", 'messages')
        reqsh.setProp("value", str(hourly))

        reqsd = q.newChild(None, "stat", None)
        reqsd.setProp("name", 'messages/daily')
        reqsd.setProp("units", 'messages')
        reqsd.setProp("value", str(daily))

        reqsu = q.newChild(None, "stat", None)
        reqsu.setProp("name", 'messages/users')
        reqsu.setProp("units", 'users')
        reqsu.setProp("value", str(users))

        self.stream.send(iq)
        return 1

    def message(self, iq):
        body = iq.get_body()
        if body == None or body == '':
            print("Got no msg")
            return False
        body = body.strip()
        fromjid = iq.get_from().bare()
        tojid = iq.get_to().bare()
        feedname = iq.get_to().node
        print("Got message from " + str(fromjid) + ": " + body.encode("utf-8"))
        if fromjid not in self.msgstat:
            self.msgstat[fromjid] = list()

        fast = False
        ts = time.time()
        daily = 0

        for jid in self.msgstat:
            for stamp in self.msgstat[jid]:
                if stamp > ts - 86400:
                    daily += 1
                else:
                    self.msgstat[jid].remove(stamp)

        for mt in self.msgstat[fromjid]:
            if mt > ts - self.tpr and len(self.msgstat[fromjid]) > 0: # 3 seconds beetween messages
                fast = True

        if fast:
            self.sendmsg(tojid, fromjid, 'Too fast! Wait a moment...')
        elif daily > self.tpd:
            self.sendmsg(tojid, fromjid, 'Daily limit reached, try later')
        else:
            self.msgstat[fromjid].append(time.time())
            if self.checklang(feedname) and len(body) < 8192:
                feedsplit = feedname.split(str(2))
                while self.lastmsg > time.time() - self.tpr:
                    time.sleep(0.1)
                self.lastmsg = time.time()
                self.sendmsg(tojid, fromjid, self.trans(feedsplit[0], feedsplit[1], body))
            else:
                print("Wrong language or message too long")

    def disco_get_items(self, node, iq):
        return self.browseitems(iq, node)

    def disco_get_info(self,node,iq):
        return self.disco_info

    def sendmsg(self, fromjid, tojid, msg):
        m = Message(to_jid = tojid, from_jid = JID(str(fromjid) + "/gtt"), stanza_type = 'chat', body = msg)
        self.stream.send(m)

    def browseitems(self, iq=None, node=None):
        disco_items = DiscoItems()
        fromjid = iq.get_from().bare()
        newjid = JID(domain=self.name)
        if node == None and iq.get_to().node == None:
            item = DiscoItem(disco_items, newjid, name="Languages list",  node="list")
        if node == 'list':
            for fr in sorted(self.LANGUAGES):
                item = DiscoItem(disco_items, newjid, name = self.LANGUAGES[fr].capitalize(), node = ' ')
        return disco_items

    def pingpong(self, iq):
        iq = iq.make_result_response()
        self.stream.send(iq)
        return 1

    def get_time(self, iq):
        iq = iq.make_result_response()
        q = iq.xmlnode.newChild(None, "time", None)
        q.setProp("xmlns", "urn:xmpp:time")
        q.newTextChild(q.ns(), "tzo", "+02:00")
        q.newTextChild(q.ns(), "utc", time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
        self.stream.send(iq)
        return 1

    def get_last(self, iq):
        iq = iq.make_result_response()
        q = iq.new_query("jabber:iq:last")
#        if iq.get_from() == self.name:
#            q.setProp("seconds", str(int(time.time()) - self.start_time))
#        else:
        print(self.lastmsg)
        q.setProp("seconds", str(int(time.time() - self.lastmsg)))
        self.stream.send(iq)
        return 1

    def get_register(self,iq):
        if iq.get_to() != self.name:
            self.stream.send(iq.make_error_response("feature-not-implemented"))
            return
        if not iq.get_from().bare():
            self.stream.send(iq.make_error_response("not-acceptable"))
            return
        iq=iq.make_result_response()
        q=iq.new_query("jabber:iq:register")
        form=q.newChild(None,"x",None)
        form.setProp("xmlns","jabber:x:data")
        form.setProp("type","form")
        form.newTextChild(None,"title","New Google Translate bot registration")

# https://xmpp.org/extensions/xep-0004.html
        fromlang = form.newChild(None, "field", None)
        fromlang.setProp("type", "list-single")
        fromlang.setProp("var", "fromlang")
        fromlang.setProp("label", "From")
        fromlang.newChild(None, "value", "auto")

        fromopt = fromlang.newChild(None, "option", None)
        fromopt.setProp("label", "Auto")
        fromopt.newChild(None, "value", 'auto')
        for f in sorted(self.LANGUAGES):
            fromopt = fromlang.newChild(None, "option", None)
            fromopt.setProp("label", self.LANGUAGES[f].capitalize())
            fromopt.newChild(None, "value", f)

        tolang = form.newChild(None, "field", None)
        tolang.setProp("type", "list-single")
        tolang.setProp("var", "tolang")
        tolang.setProp("label", "To")
        tolang.newChild(None, "value", "en")

        for t in sorted(self.LANGUAGES):
            toopt = tolang.newChild(None, "option", None)
            toopt.setProp("label", self.LANGUAGES[t].capitalize())
            toopt.newChild(None, "value", t)

        self.stream.send(iq)

    def set_register(self,iq):
        if iq.get_to() != self.name:
            self.stream.send(iq.make_error_response("feature-not-implemented"))
            return

        # check for returned vars
        fromlang = iq.xpath_eval("//r:field[@var='fromlang']/r:value",{"r":"jabber:x:data"})
        tolang = iq.xpath_eval("//r:field[@var='tolang']/r:value",{"r":"jabber:x:data"})
        if not fromlang and not tolang:
            self.stream.send(iq.make_error_response("not-acceptable"))
            return
        fromlang = fromlang[0].getContent()
        tolang   = tolang[0].getContent()
        if fromlang == tolang:
            self.stream.send(iq.make_error_response("not-acceptable"))
            return
        iqres = iq.make_result_response()
        self.stream.send(iqres)
        pres = Presence(stanza_type="subscribe", from_jid=JID(unicode(fromlang + "2" + tolang, 'utf-8') + '@' + self.name), to_jid=iqres.get_to().bare())
        self.stream.send(pres)

    def get_vCard(self,iq):

        iqmr=iq.make_result_response()
        q=iqmr.xmlnode.newChild(None,"vCard",None)
        q.setProp("xmlns","vcard-temp")

        transav=q.newTextChild(None,"PHOTO", None)
        transav.newTextChild(None, "BINVAL", self.gttlogo)
        transav.newTextChild(None, "TYPE", 'image/png')

        q.newTextChild(None,"BDAY","2022-12-07")
        q.newTextChild(None,"URL","https://github.com/jabberworld/gtrans")

        if iq.get_to() == self.name:
            q.newTextChild(None,"FN","Google Translate Transport")
            q.newTextChild(None,"NICKNAME","Google Translate")
            q.newTextChild(None,"DESC","Google Translate Transport")
            q.newTextChild(None,"ROLE","Создаю ботов для получения перевода текста через Google Translate")
        else:
            # vcard for bot
            nick = iqmr.get_from().node
            if self.checklang(nick):
                nicksplit = nick.split(str(2))
                if nicksplit[0] == 'auto':
                    fromlang = 'Auto'
                else:
                    fromlang = self.LANGUAGES[nicksplit[0]].capitalize()

                tolang = self.LANGUAGES[nicksplit[1]].capitalize()
                q.newTextChild(None,"FN","Google Translate Bot")

                if fromlang == 'Auto':
                    q.newTextChild(None,"NICKNAME", "Auto to " + tolang)
                    q.newTextChild(None,"ROLE", "Перевожу любой текст на " + tolang + " через Google Translate")
                    q.newTextChild(None,"DESC", "Бот-переводчик любого текста на " + tolang)
                else:
                    q.newTextChild(None,"NICKNAME", fromlang + " to " + tolang)
                    q.newTextChild(None,"ROLE", "Перевожу текст с " + fromlang + " на " + tolang + " через Google Translate")
                    q.newTextChild(None,"DESC", "Бот-переводчик текста с " + fromlang + " на " + tolang)

        self.stream.send(iqmr)
        return 1

    def get_version(self,iq):
        global programmVersion
        iq=iq.make_result_response()
        q=iq.new_query("jabber:iq:version")
        q.newTextChild(q.ns(), "name", "Google Translate Transport")
        q.newTextChild(q.ns(), "version", programmVersion)
        q.newTextChild(q.ns(), "os", "Python "+sys.version.split()[0]+" + PyXMPP")
        self.stream.send(iq)
        return 1

    def presence(self, stanza):
        feedname=stanza.get_to().node
        if feedname==None:
            return None
        if stanza.get_type()=="unavailable":
            p=Presence(from_jid=stanza.get_to(),to_jid=stanza.get_from(),stanza_type="unavailable")
            self.stream.send(p)
        if (stanza.get_type() == "available" or stanza.get_type() == None) and self.checklang(feedname):
            p=Presence(from_jid=JID(stanza.get_to().as_unicode()+'/gtt'),
                        to_jid=stanza.get_from(),
                        show=self.get_show(feedname),
                        status=self.get_status(feedname))
            self.stream.send(p)

    def get_show(self, feedname):
        st = None
        return st

    def get_status(self, feedname):
        status = 'Lets translate to ' + self.LANGUAGES[feedname.split(str(2))[1]].capitalize()
        return status

    def presence_control(self, stanza):
        feedname = stanza.get_to().node
        fromjid = stanza.get_from().bare()
        print("Got "+str(stanza.get_type())+" request from "+str(fromjid)+" to"),
        print(feedname)
        if stanza.get_type()=="subscribe":
            p=Presence(stanza_type="subscribe",
                to_jid=fromjid,
                from_jid=stanza.get_to())
            self.stream.send(p)
            p=Presence(stanza_type="subscribed",
                to_jid=fromjid,
                from_jid=stanza.get_to())
            self.stream.send(p)
            return 1

        if stanza.get_type()=="unsubscribe" or stanza.get_type()=="unsubscribed":
            p=Presence(stanza_type="unsubscribe",
                to_jid=fromjid,
                from_jid=stanza.get_to())
            self.stream.send(p)
            p=Presence(stanza_type="unsubscribed",
                to_jid=fromjid,
                from_jid=stanza.get_to())
            self.stream.send(p)

while True:
    try:
        print("Connecting to server")
# https://xmpp.org/registrar/disco-categories.html
        c=Component(JID(NAME), PASSWORD, HOST, int(PORT), disco_category='automation', disco_type="translation", disco_name="Google Translate Transport")
        c.connect()
        print("Connected")
        c.loop(1)
        time.sleep(1) # to prevent fast reconnects in case of auth problems
    except KeyboardInterrupt:
        print("Keyboard interrupt, shutting down")
        c.disconnect()
        sys.exit()
    except Exception as ae:
        print(ae)
        print("Lost connection to server, reconnect in 60 seconds")
        time.sleep(60)
        pass
