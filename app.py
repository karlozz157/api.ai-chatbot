#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import random

from crawlers import SongCrawler

from flask import Flask
from flask import request
from flask import make_response

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    res = SearchSong().process_request(req)
    res = json.dumps(res, indent=4)
    res = make_response(res)
    res.headers['Content-Type'] = 'application/json'
    return res

class SearchSong(object):
    ERROR_MESSAGE = 'por favor, inténtelo de nuevo'

    def process_request(self, req):
        try:
            song = self.__get_song(req)
            speech = self.__get_speech(song)
        except Exception as e:
            print(e.message)
            speech = self.ERROR_MESSAGE
        return {
            'speech': speech,
            'displayText': speech
        }

    def __get_speech(self, song):
        phrases = self.__get_phrases()
        phrase_index = random.randrange(0, (len(phrases)))
        return phrases[phrase_index] % (song['name'], song['url'])

    def __get_song(self, req):
        result = req.get('result')
        parameters = result.get('parameters')
        artist = parameters.get('music-artist')
        return SongCrawler.search(artist)

    def __get_phrases(self):
        return [
            'Hello, listen "%s" - %s',
            'You should listen "%s" - %s'
            'Listen "%s" is very good! - %s',
            'Have you listened "%s" ? - %s'
        ]

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
