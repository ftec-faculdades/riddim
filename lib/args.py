import os
import re
import sys
from argparse import ArgumentParser

from lib.config import Config

class Args(object):

    def __init__(self):
        self.config = Config().config
        parser      = ArgumentParser()

        # server controls a la apachectl
        signals = ["stop", "start", "restart"]
        mg = parser.add_mutually_exclusive_group()
        mg.add_argument("-k", "--signal",
                                help="signal stop/start/status",
                                choices=signals,
                                default=False)

        # playlist manipulation
        parser.add_argument("-c", "--clear",
                                help="clear playlist of tracks matching REGEX",
                                metavar="REGEX")
        parser.add_argument("-i", "--index",
                                help="set now playing to index INDEX",
                                type=int,
                                metavar="INDEX")
        parser.add_argument("-q", "--query",
                                action="store_true",
                                default=False,
                                help="display server state")
        parser.add_argument("-e", "--enqueue",
                                metavar="/PATH/TO/TRACKS",
                                help="enqueue track(s)", nargs="+")
        # TODO
        #         '-R' : ['--repeat',     'toggle repeat',            'store_true',   False],
        #         '-S' : ['--shuffle',    'toggle shuffle',           'store_true',   False],

        self.args       = parser.parse_args()
        self.args_dict  = vars(self.args)

        # remove null (unselected) options
        for op, arg in self.args_dict.items():
            if not arg: del self.args_dict[op]

        if len(self.args_dict.keys()) == 0:
            # bail on no arguments
            parser.print_help()
            sys.exit(-1)

    # expose self.args to external classes
    def __getattr__(self, attr):
        try:
            return self.args.__dict__[attr]
        except KeyError:
            return None


    def __repr__(self):
        return dict(vars(self.args))