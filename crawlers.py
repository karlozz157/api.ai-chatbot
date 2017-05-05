#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
import sys
import unicodedata

from bs4 import BeautifulSoup

class Crawler(object):
    HEADERS = 0
    CONTENT = 1
    HTML_PARSER = 'html.parser'
    STATUS_OK = '200'

    def _make_request(self, url):
        url = self.__add_to(url, '\\', ['?', '&', '='])
        response = self.__shell_exec('curl -s -i %s' % url)
        response = self.__parse_response(response)
        if self.STATUS_OK in response['headers'].split('\n')[0]:
            return response['content']
        raise Exception(response['headers'])

    def _remove_accents(self, text):
        nfkd_form = unicodedata.normalize('NFKD', text)
        only_ascii = nfkd_form.encode('ASCII', 'ignore')
        return only_ascii

    def _remove_invalid_chars(self, text):
        invalid_chars = ['(', ')', '"', "'"]
        for invalid_char in invalid_chars:
            text = text.replace(invalid_char, '')
        return text

    def _replace_spaces_by_plus(self, text):
        return text.replace(' ', '+')

    def __add_to(self, text, to_add, in_chars):
        for char in in_chars:
            text = text.replace(char, '%s%s' % (to_add, char))
        return text

    def __parse_response(self, response):
        response = response.split('<html')
        headers = response[self.HEADERS].strip().split('\r\n\r\n')
        content = headers.pop().replace('>', '') + response[self.CONTENT]
        return {'headers': headers.pop(), 'content': content}

    def __shell_exec(self, cmd):
        return os.popen(cmd).read()


class Top50SongsCrawler(Crawler):
    URL = 'http://www.top50songs.org'

    def search(self, artist):
        """ search the artist's songs and only return one """
        artist = [word.capitalize() for word in artist.split(' ')] 
        artist = ' '.join(artist)
        self.artist = self._replace_spaces_by_plus(artist)
        response = self._make_request('%s/artist.php?artist=%s' % (self.URL, self.artist))
        songs = self.__get_songs_from_response(response)
        return self.__get_only_one_song(songs)

    def __get_songs_from_response(self, response):
        """ get all songs as list from html """
        soup = BeautifulSoup(response, self.HTML_PARSER)
        songs_list = []
        for song in soup.find_all('li'):
            song_text = song.get_text()
            song_text = song_text[(song_text.find('.') + 1): len(song_text)].strip()
            songs_list.append(song_text)
        return songs_list

    def __get_only_one_song(self, songs):
        """ choose  song in random way """
        choose_song = random.randrange(1, (len(songs) + 1))
        song_chosen = None
        count = 0
        for song in songs:
            count += 1
            if choose_song != count:
                continue
            song_chosen = song
            break
        song = '%s - %s' % (self.artist, song_chosen)
        return self.__apply_filters(song)

    def __apply_filters(self, song):
        """ apply filters to song like remove accents or invalid chars """
        song = self._replace_spaces_by_plus(song)
        song = self._remove_invalid_chars(song)
        song = self._remove_accents(song)
        return song


class YoutubeCrawler(Crawler):
    URL = 'https://www.youtube.com'

    def search(self, to_search):
        """ search something in youtube and return the first result """
        response = self._make_request('%s/results?search_query=%s' % (self.URL, to_search))
        return self.__get_first_result_from_response(response, to_search)

    def __get_first_result_from_response(self, response, to_search):
        """ parse the first result from html """
        soup = BeautifulSoup(response, self.HTML_PARSER)
        results_div = soup.find(id="results")
        for ol in results_div.find_all('ol'):
            try:
                if 'item-section' in ol.get('id'):
                    url = self.__get_video_url(ol)
                    return {'name': to_search.replace('+', ' '), 'url': url}
            except Exception as e:
                print e

    def __get_video_url(self, ol):
        """ get url from first video """
        for li in ol.find_all('li'):
            links = li.find_all('a')
            if links and 3 == len(links):
                return '%s%s' % (self.URL, links[1].get('href'))


class ScrappyCrawler(object):
    MAX_ATTEMPTS = 3

    @classmethod
    def search(cls, artist):
        attempts = 0
        try_again = True
        while try_again:
            try:
                top50SongsCrawler = Top50SongsCrawler()
                song = top50SongsCrawler.search(artist)
                youtubeCrawler = YoutubeCrawler()
                return youtubeCrawler.search(song)
            except Exception as e:
                print e
                attempts += 1
                if attempts == cls.MAX_ATTEMPTS:
                    try_again = False
