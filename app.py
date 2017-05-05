#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import random

from crawlers import ScrappyCrawler

from flask import Flask
from flask import request
from flask import make_response

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    res = make_response(res)
    res.headers['Content-Type'] = 'application/json'
    return res

def processRequest(req):
    song = get_song(req)
    res = makeWebhookResult(song)
    return res

def get_song(req):
    result = req.get('result')
    parameters = result.get('parameters')
    artist = parameters.get('music-artist')
    if artist is None:
        return None
    return ScrappyCrawler.search(artist)

def makeWebhookResult(song):
    phrases = get_phrases()
    phrase_index = random.randrange(0, (len(phrases)))
    speech = phrases[phrase_index] % (song['name'], song['url'])
    return {
        "speech": speech,
        "displayText": speech,
    }

def get_phrases():
    return [
        'Hello, listen "%s" - %s',
        'You should listen "%s" - %s'
        'Listen "%s" - %s!',
        'Listen "%s" is very good! - %s',
        'Have you listened "%s" ? - %s'
    ]

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
