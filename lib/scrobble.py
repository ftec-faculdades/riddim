# -*- coding: utf-8 -*-
import threading
import time
import os
import datetime
import sys
import Queue
import hashlib
from urllib import unquote
import ConfigParser

try:
    import scrobbler
except ImportError:
    print u"""Oops.  You need to run:\n\
    % pip install scrobbler"""
    sys.exit(-1)

from lib.logger import log
from lib.config import Config

NOW_PLAYING, PLAYED = 0, 1


class ScrobbleItem:

    def __init__(self, scrobble_type, song):
        self.type = scrobble_type
        self.song = song
        #
        self.error = False
        self.etime = None


def escape(str):
    return unquote(str)


class Scrobbler(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.daemon = True

    def login(self):
        config = ConfigParser.ConfigParser()
        cwd = os.path.realpath(os.path.dirname(__file__) + u'/..')
        config.read(os.path.join(cwd, u'scrobbler.cfg'))
        username = config.get(u'scrobbler', u'username')
        password = hashlib.md5(config.get(u'scrobbler', u'password')).hexdigest()
        try:
            scrobbler.login(user=username, password=password)
        except scrobbler.ProtocolError:
            time.sleep(49)
        except Exception as e:
            log.exception(u"Couldn't login: %s" % e)

    def run(self):
        # well this is just fugly.  call it "experimental"
        while Config.running:
            try:
                scrobble_item = self.queue.get(0)
                try:
                    song = scrobble_item.song
                    type = scrobble_item.type
                    error = scrobble_item.error
                    etime = scrobble_item.etime

                    (tracknumber, artist, album, track) = [escape(item) for item in song.tags]

                    if type == NOW_PLAYING:
                        log.debug(u"scrobbling now playing %s %s %s" %
                                (artist, track, album))
                        self.login()
                        scrobbler.now_playing(
                                artist,
                                track)
                        # now_playing auto flushes, apparently.  don't call
                        # flush here or it will throw an exception, which is not
                        # what we want.
                    elif type == PLAYED:
                        # See: http://exhuma.wicked.lu/projects/python/scrobbler/api/public/scrobbler-module.html#login
                        # if mimetype is wrong, length == 0
                        if song.length < 30: log.warn(u"song length %s" % song.length)

                        # wait 60 seconds before re-trying
                        # submission
                        if error:
                            if (time.time() - etime) < 60:
                                break
                        log.debug(u"scrobbling played %s %s %s %s" %
                                (artist, track, album, song.length))
                        self.login()
                        scrobbler.submit(
                            artist,
                            track,
                            int(time.mktime(datetime.datetime.now().timetuple())),
                            source=escape(u'P'),
                            length=song.length,
                            album=album)
                        scrobbler.flush()
                except Exception as e:
                    log.exception(u"scrobble error: %s" % e)
                    # put it back
                    scrobble_item.error = True
                    scrobble_item.etime = time.time()
                    self.queue.put(scrobble_item)
            except Queue.Empty:
                pass

            # AS API enforced limit -- do not change.
            time.sleep(10)
