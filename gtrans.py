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

programmVersion="1.2.5"

config=os.path.abspath(os.path.dirname(sys.argv[0]))+'/config.xml'

dom = xml.dom.minidom.parse(config)

NAME =  dom.getElementsByTagName("name")[0].childNodes[0].data
HOST =  dom.getElementsByTagName("host")[0].childNodes[0].data
PORT =  dom.getElementsByTagName("port")[0].childNodes[0].data
PASSWORD = dom.getElementsByTagName("password")[0].childNodes[0].data

# Throttle limits
TPR =  dom.getElementsByTagName("tpr")[0].childNodes[0].data
TPD =  dom.getElementsByTagName("tpd")[0].childNodes[0].data

DEBUG =  dom.getElementsByTagName("debug")[0].childNodes[0].data

class Component(pyxmpp.jabberd.Component):
    start_time = int(time.time())
    msgstat = {} # list of requests per JID
    lastmsg = start_time # last request marker
    name = NAME
    debug = int(DEBUG)
    tpr = int(TPR) # throttle by request per second
    tpd = int(TPD) # throttle by request per day
    jidseen = {} # list of jids
    gttlogo = 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAFdklEQVR42r2XBWwbWRCGW7FOzMdiDnl3YwxdfWGqw1ymJKKSoMzMzMzc4zIzM3MTwzHu2l7/Nx51Tz6ZtilY+sye+Xf+ee+NO4mi+JFgSJ4sGJLO0+MV4rIOrgiC4Qj9NpHo9EY3CrTGlFniz6qfhi+6zdNH02wYM4tBQgaLgkAxhI4LEEXp7+zmrXDM9sMxy6sTH7IaZgQF7KMKfEC8gYBUE/IGHeKgjpn/EHIc/mEReUOOQzLaPIIhRaDbmwo4+EqArJuSSS6Ys+sgpCQOCgrgKrw3AYxCNkwL2nAiOTm5ICkpKUcnuYTdYDB8bjKZOndQgGbDMbLBGsjKylLy8vKU3NxcXdjtdlmSpOtUOUdUAV1nyCid8Q9Kpv8Hv+5KhNpgstdgwvhxuHLlCi5duqSLc+fOYejQoaAq3IsogJJwsp5LZEzZ68WKwz7M+taLASv4M0azIb12Cvr26YWnT5+ivb1dF263G7t27YLRaAyECdASTNrjxSOXCuevAdxrV/HiZxVtPwew9KAXFbP5e2xD7uCj6JKdh5MnT8DpdKKtrS0e/L09e/aAegBhAkqp1MO3KnD/FsA3l/0YsFJB7TwZvZbKWHvMh0uPVfRYzPZwBUomOmG2V2PRwgUc+OXLlx0WwFdVSVd35r4fJ+76UTVHZu+Lp/2DIiL4vG6+HNYL6TWT0YdsePLkCScgEWGPegRw4D7LZLz8WWXvKTGLmPa1F8sO+bj8QeZ+70XTwhAbBh2BnWw4deokXC4XJ7h8+TKmTJmCO3fu8GvN/1gCuPzNKxX2fdR2hQU0UqLjd/x44FS5F556VPytBDBim8IVCbVhzuxZuHXrFm7evIlt27YhOzsbP/zwA7++fv06c//+/dgWNCyQcZ+SrT/howRcalTPlbn0wcc533nhov5oXa2wYM2GzLopyEi3obS0lKF9AWazGQUFBSgpKUFRUREzcuRItiSKAPYXa6jZ2n8JcDMGXxe/8r9llYK7bSr2X/ejfNYrCwjelAYdhjUtk6owGzt37sT27duZzZs3o6KiAvX19diyZQuOHj0acxVw0Hq62kM3/bwSvqWVsOSAFzvO+vDiJxVXn6rot1xbBTIYtqGdbVi8aCEtyZN4/PgxfvzxRxw5cgS0+7EYj8fDfRBLAMHBeekt2OfFxUcqHrpUXHumYu1xX8gSlMPIqJmI2ppqVFZWYurUqXj06BFaW1vRr18/fh57FYRtxVx2XpZUEV4N5Hnk5NpqGHgI2TkFmDBhAvLz8zFo0CB+3Ldvn7ZH6BWgiWAhIcQ4oNiGNrKhCksWL8LYsWORmJjITfc6O+Ebk149AU2N9ejVqxdsNhvq6upw4cIF/RXoMGyDj2MJkgkV5eXYu3cvunfvzmJu3LjBDUgiIgk49OYCNBsmtMGYVY5ZM2dw1585c4aXYUtLC29S4RWQTIHcgQfgmK1ygDfHSzaMR/OA/nxEUzJe+1VVVVi3bh2//p8AQTDcy6gcgaJRd1E89tGbM+4J7P024svsXLr609DOgGvXruHu3bvhFQiORTSaX0+1ZcvG9HzlNVGN6QUwZhSFUIxUWw6k1FQ+D7QZQTuIIvVAZ6rC50JKkp0m3FwiRyfZgiFpm2QtgqlkDkylC4iFMOaPgkG0YgBZQIdQ/HmgIzdtDBeEZIdo6qJYKrfA2nAElqodEGxV6NmzJ65evap1/RsKiCGC+ISE3DIVToSlejeEtBo01Ieve40wC95cgET2pSyW0qsgZTSipqYG586d5aGTkkSDh5ZVq1ZBkqS/3+A/pahVwSGIokLB0NzcjOnTp/NBFItx48ahsLDQT2P5Gg72ZlUQP6LH3SToKgW8TP+S4nGFOJ+SkjKJfvPRvxq8CCnBwq3aAAAAAElFTkSuQmCC'

# wget -qO- https://translate.google.com/ | sed '/[[[/,/]]]/s/\],\[/\n/g' | awk '{if (p==1) {v=$0; gsub(/]/, "", v); gsub(/"/, "'\''", v); gsub(/,/, ": ", v); gsub(/$/, ",", v); print v}}; /]/{p=0} /"auto","Detect language"/{p=1}'
    LANGUAGES = {
'ab': 'Abkhaz',
'ace': 'Acehnese',
'ach': 'Acholi',
'aa': 'Afar',
'af': 'Afrikaans',
'sq': 'Albanian',
'alz': 'Alur',
'am': 'Amharic',
'ar': 'Arabic',
'hy': 'Armenian',
'as': 'Assamese',
'av': 'Avar',
'awa': 'Awadhi',
'ay': 'Aymara',
'az': 'Azerbaijani',
'ban': 'Balinese',
'bal': 'Baluchi',
'bm': 'Bambara',
'bci': 'Baoulé',
'ba': 'Bashkir',
'eu': 'Basque',
'btx': 'Batak Karo',
'bts': 'Batak Simalungun',
'bbc': 'Batak Toba',
'be': 'Belarusian',
'bem': 'Bemba',
'bn': 'Bengali',
'bew': 'Betawi',
'bho': 'Bhojpuri',
'bik': 'Bikol',
'bs': 'Bosnian',
'br': 'Breton',
'bg': 'Bulgarian',
'bua': 'Buryat',
'yue': 'Cantonese',
'ca': 'Catalan',
'ceb': 'Cebuano',
'ch': 'Chamorro',
'ce': 'Chechen',
'ny': 'Chichewa',
'zh-CN': 'Chinese (Simplified)',
'zh-TW': 'Chinese (Traditional)',
'chk': 'Chuukese',
'cv': 'Chuvash',
'co': 'Corsican',
'crh': 'Crimean Tatar',
'hr': 'Croatian',
'cs': 'Czech',
'da': 'Danish',
'fa-AF': 'Dari',
'dv': 'Dhivehi',
'din': 'Dinka',
'doi': 'Dogri',
'dov': 'Dombe',
'nl': 'Dutch',
'dyu': 'Dyula',
'dz': 'Dzongkha',
'en': 'English',
'eo': 'Esperanto',
'et': 'Estonian',
'ee': 'Ewe',
'fo': 'Faroese',
'fj': 'Fijian',
'tl': 'Filipino',
'fi': 'Finnish',
'fon': 'Fon',
'fr': 'French',
'fy': 'Frisian',
'fur': 'Friulian',
'ff': 'Fulani',
'gaa': 'Ga',
'gl': 'Galician',
'ka': 'Georgian',
'de': 'German',
'el': 'Greek',
'gn': 'Guarani',
'gu': 'Gujarati',
'ht': 'Haitian Creole',
'cnh': 'Hakha Chin',
'ha': 'Hausa',
'haw': 'Hawaiian',
'iw': 'Hebrew',
'hil': 'Hiligaynon',
'hi': 'Hindi',
'hmn': 'Hmong',
'hu': 'Hungarian',
'hrx': 'Hunsrik',
'iba': 'Iban',
'is': 'Icelandic',
'ig': 'Igbo',
'ilo': 'Ilocano',
'id': 'Indonesian',
'ga': 'Irish',
'it': 'Italian',
'jam': 'Jamaican Patois',
'ja': 'Japanese',
'jw': 'Javanese',
'kac': 'Jingpo',
'kl': 'Kalaallisut',
'kn': 'Kannada',
'kr': 'Kanuri',
'pam': 'Kapampangan',
'kk': 'Kazakh',
'kha': 'Khasi',
'km': 'Khmer',
'cgg': 'Kiga',
'kg': 'Kikongo',
'rw': 'Kinyarwanda',
'ktu': 'Kituba',
'trp': 'Kokborok',
'kv': 'Komi',
'gom': 'Konkani',
'ko': 'Korean',
'kri': 'Krio',
'ku': 'Kurdish (Kurmanji)',
'ckb': 'Kurdish (Sorani)',
'ky': 'Kyrgyz',
'lo': 'Lao',
'ltg': 'Latgalian',
'la': 'Latin',
'lv': 'Latvian',
'lij': 'Ligurian',
'li': 'Limburgish',
'ln': 'Lingala',
'lt': 'Lithuanian',
'lmo': 'Lombard',
'lg': 'Luganda',
'luo': 'Luo',
'lb': 'Luxembourgish',
'mk': 'Macedonian',
'mad': 'Madurese',
'mai': 'Maithili',
'mak': 'Makassar',
'mg': 'Malagasy',
'ms': 'Malay',
'ms-Arab': 'Malay (Jawi)',
'ml': 'Malayalam',
'mt': 'Maltese',
'mam': 'Mam',
'gv': 'Manx',
'mi': 'Maori',
'mr': 'Marathi',
'mh': 'Marshallese',
'mwr': 'Marwadi',
'mfe': 'Mauritian Creole',
'chm': 'Meadow Mari',
'mni-Mtei': 'Meiteilon (Manipuri)',
'min': 'Minang',
'lus': 'Mizo',
'mn': 'Mongolian',
'my': 'Myanmar (Burmese)',
'nhe': 'Nahuatl (Eastern Huasteca)',
'ndc-ZW': 'Ndau',
'nr': 'Ndebele (South)',
'new': 'Nepalbhasa (Newari)',
'ne': 'Nepali',
'bm-Nkoo': 'NKo',
'no': 'Norwegian',
'nus': 'Nuer',
'oc': 'Occitan',
'or': 'Odia (Oriya)',
'om': 'Oromo',
'os': 'Ossetian',
'pag': 'Pangasinan',
'pap': 'Papiamento',
'ps': 'Pashto',
'fa': 'Persian',
'pl': 'Polish',
'pt': 'Portuguese (Brazil)',
'pt-PT': 'Portuguese (Portugal)',
'pa': 'Punjabi (Gurmukhi)',
'pa-Arab': 'Punjabi (Shahmukhi)',
'qu': 'Quechua',
'kek': 'Qʼeqchiʼ',
'rom': 'Romani',
'ro': 'Romanian',
'rn': 'Rundi',
'ru': 'Russian',
'se': 'Sami (North)',
'sm': 'Samoan',
'sg': 'Sango',
'sa': 'Sanskrit',
'sat-Latn': 'Santali',
'gd': 'Scots Gaelic',
'nso': 'Sepedi',
'sr': 'Serbian',
'st': 'Sesotho',
'crs': 'Seychellois Creole',
'shn': 'Shan',
'sn': 'Shona',
'scn': 'Sicilian',
'szl': 'Silesian',
'sd': 'Sindhi',
'si': 'Sinhala',
'sk': 'Slovak',
'sl': 'Slovenian',
'so': 'Somali',
'es': 'Spanish',
'su': 'Sundanese',
'sus': 'Susu',
'sw': 'Swahili',
'ss': 'Swati',
'sv': 'Swedish',
'ty': 'Tahitian',
'tg': 'Tajik',
'ber-Latn': 'Tamazight',
'ber': 'Tamazight (Tifinagh)',
'ta': 'Tamil',
'tt': 'Tatar',
'te': 'Telugu',
'tet': 'Tetum',
'th': 'Thai',
'bo': 'Tibetan',
'ti': 'Tigrinya',
'tiv': 'Tiv',
'tpi': 'Tok Pisin',
'to': 'Tongan',
'ts': 'Tsonga',
'tn': 'Tswana',
'tcy': 'Tulu',
'tum': 'Tumbuka',
'tr': 'Turkish',
'tk': 'Turkmen',
'tyv': 'Tuvan',
'ak': 'Twi',
'udm': 'Udmurt',
'uk': 'Ukrainian',
'ur': 'Urdu',
'ug': 'Uyghur',
'uz': 'Uzbek',
've': 'Venda',
'vec': 'Venetian',
'vi': 'Vietnamese',
'war': 'Waray',
'cy': 'Welsh',
'wo': 'Wolof',
'xh': 'Xhosa',
'sah': 'Yakut',
'yi': 'Yiddish',
'yo': 'Yoruba',
'yua': 'Yucatec Maya',
'zap': 'Zapotec',
'zu': 'Zulu'
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
                if self.debug == 1:
                    print("Got answer: " + translated_text.encode("utf-8"))
                return translated_text
        except:
            return "Translation error"

# check if languages from node in JID match languages list
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
        hourly = daily = users = active = 0
        for jid in self.msgstat:
            active += 1
            for stamp in self.msgstat[jid]:
                if stamp > ts - 86400:
                    daily += 1
                    if stamp > ts - 3600:
                        hourly += 1
                else:
                     self.msgstat[jid].remove(stamp)
            if len(self.msgstat[jid]) > 0:
                users += 1

        reqsh = q.newChild(None, "stat", None)
        reqsh.setProp("name", 'messages/hourly')
        reqsh.setProp("units", 'messages')
        reqsh.setProp("value", str(hourly))

        reqsd = q.newChild(None, "stat", None)
        reqsd.setProp("name", 'messages/daily')
        reqsd.setProp("units", 'messages')
        reqsd.setProp("value", str(daily))

        reqsu = q.newChild(None, "stat", None)
        reqsu.setProp("name", 'users/daily')
        reqsu.setProp("units", 'users')
        reqsu.setProp("value", str(users))

        reqsa = q.newChild(None, "stat", None)
        reqsa.setProp("name", 'users/active')
        reqsa.setProp("units", 'users')
        reqsa.setProp("value", str(active))

        reqst = q.newChild(None, "stat", None)
        reqst.setProp("name", 'users/total')
        reqst.setProp("units", 'users')
        reqst.setProp("value", str(len(self.jidseen)))

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
        direction = iq.get_to().node
        self.jidseen[fromjid] = 1
        if self.debug == 1:
            print("Got message from " + str(fromjid) + ": " + body.encode("utf-8"))
            print(len(self.jidseen)),
            print(self.jidseen)
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
            if self.checklang(direction) and len(body) < 8192:
                dirsplit = direction.split(str(2))
                while self.lastmsg > time.time() - self.tpr:
                    time.sleep(0.1)
                self.lastmsg = time.time()
                self.sendmsg(tojid, fromjid, self.trans(dirsplit[0], dirsplit[1], body))
            else:
                print("Wrong language or message too long")

    def disco_get_items(self, node, iq):
        return self.browseitems(iq, node)

    def disco_get_info(self,node,iq):
        return self.disco_info

    def sendmsg(self, fromjid, tojid, msg):
        m = Message(to_jid = tojid, from_jid = JID(str(fromjid) + "/gtt"), stanza_type = 'chat', body = msg)
        self.stream.send(m)

    def mknode(self, disco_items, name, desc):
        desc = name+" ("+desc+")"
        newjid = JID(name, self.name)
        item = DiscoItem(disco_items, newjid, name=desc, node=None)

    def browseitems(self, iq=None, node=None):
        disco_items = DiscoItems()
        fromjid = iq.get_from().bare()
        newjid = JID(domain=self.name)
        if node == None and iq.get_to().node == None:
            item = DiscoItem(disco_items, newjid, name="Languages list (total: " + str(len(self.LANGUAGES)) + ")",  node="list")
            item = DiscoItem(disco_items, newjid, name="From language",   node="from")
        if node == 'list':
            for fr in sorted(self.LANGUAGES):
                item = DiscoItem(disco_items, newjid, name = unicode(self.LANGUAGES[fr].capitalize(), 'utf-8'), node = ' ')
        if node == 'from':
            item = DiscoItem(disco_items, newjid, name = "Auto", node = 'auto')
            for fr in sorted(self.LANGUAGES):
                item = DiscoItem(disco_items, newjid, name = unicode(self.LANGUAGES[fr].capitalize(), 'utf-8'), node = fr)
        if node in self.LANGUAGES or node == 'auto':
            for to in sorted(self.LANGUAGES):
                if node == 'auto':
                    self.mknode(disco_items, "auto2" + to, "Auto to " + unicode(self.LANGUAGES[to].capitalize(), 'utf-8'))
                elif node != to:
                    self.mknode(disco_items, node + "2" + to, unicode(self.LANGUAGES[node].capitalize(), 'utf-8') + " to " + unicode(self.LANGUAGES[to].capitalize(), 'utf-8'))
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
        if iq.get_from() == self.name:
            q.setProp("seconds", str(int(time.time()) - self.start_time))
        else:
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
        q.newTextChild(None,"URL","https://github.com/jabberworld/gtt")

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
        q.newTextChild(q.ns(), "version", programmVersion + " (" + str(len(self.LANGUAGES)) + " languages)")
        q.newTextChild(q.ns(), "os", "Python "+sys.version.split()[0]+" + PyXMPP")
        self.stream.send(iq)
        return 1

    def presence(self, stanza):
        direction=stanza.get_to().node
        to_jid = stanza.get_from()
        if direction==None:
            return None
        if stanza.get_type()=="unavailable":
            p=Presence(from_jid = stanza.get_to(), to_jid = to_jid, stanza_type="unavailable")
            self.stream.send(p)
        if (stanza.get_type() == "available" or stanza.get_type() == None) and self.checklang(direction):
            self.jidseen[to_jid.bare()] = 1
            p=Presence(from_jid = JID(stanza.get_to().as_unicode() + '/gtt'),
                        to_jid = to_jid,
                        show = self.get_show(direction),
                        status = self.get_status(direction))
            self.stream.send(p)

    def get_show(self, direction):
        st = None
        return st

    def get_status(self, direction):
        status = 'Lets translate to ' + self.LANGUAGES[direction.split(str(2))[1]].capitalize()
        return status

    def presence_control(self, stanza):
        direction = stanza.get_to().node
        fromjid = stanza.get_from().bare()
        print("Got "+str(stanza.get_type())+" request from "+str(fromjid)+" to"),
        print(direction)
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
