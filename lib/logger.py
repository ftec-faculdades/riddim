# -*- coding: utf-8 -*-
import logging
log = logging.getLogger(u"riddim")

log.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler(u"%s/../../log/riddim.log" % __file__)
ch = logging.StreamHandler()

# create console handler log level
fh.setLevel(logging.DEBUG)
ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter(u"%(asctime)s %(name)s %(filename)s %(levelname)s %(message)s")

ch.setFormatter(formatter)
fh.setFormatter(formatter)

# add the handlers to log
log.addHandler(ch)
log.addHandler(fh)
