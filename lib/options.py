import os
import re
from optparse import OptionParser

from lib.config import RiddimConfig

class RiddimOptions(object):
    def __init__(self):
        self.config = RiddimConfig(os.getcwd()).config
        self.op = OptionParser()
        self.op.disable_interspersed_args() # unix-style
        # boolean flags
        self.flags = {
                # server booleans
                '-p' : ['--play','start playback','store_true'],
                '-u' : ['--pause','pause playback','store_true'],
                '-s' : ['--stop','stop playback','store_true'],
                '-n' : ['--next','proceed to next track','store_true'],
                '-r' : ['--prev','go back to previous track','store_true'],
                '-R' : ['--repeat','toggle repeat','store_true'],
                '-S' : ['--shuffle','toggle shuffle','store_true'],
                '-Q' : ['--query','display server state','store_true'],
                '-c' : ['--clear','clear playlist','store_true'],
                # only with signals
                '-f' : ['--foreground','don\'t fork the server','store_true'],
                # non-booleans
                '-k' : ['--signal','signal stop/start/status','store'],
                '-e' : ['--enqueue','enqueue track(s) onto playlist','store']

        }
        for short,v in self.flags.iteritems():
            long, help, action = v
            self.op.add_option(short,long,action=action,help=help)

        self.op.add_option('-P','--port',action='store',help='port number to try',default=18944)

        self.options, self.args = self.op.parse_args()
        self.signal = self.check_signal()

        if self.signal:
            self.foreground = self.options.foreground
            self.port = self.options.port
        else:
            self.flag = self.check_flag()
    
    def check_signal(self):
        valid_signals = ['stop','start','restart','status']
        if self.options.signal and self.options.signal in valid_signals:
            return self.options.signal
        else:
            return False

    def check_flag(self):
        valid_flags = [re.sub('\-\-','',f[0]) for f in self.flags.values()]
        # we can get away with using eval here 
        #   . . . right?  ;)
        try:
            return [flag for flag in valid_flags if eval("self.options.%s" % flag)][0]
        except IndexError:
            self.op.print_help()
            return False
