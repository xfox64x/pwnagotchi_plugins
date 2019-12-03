__author__ = 'forrest'
__version__ = '1.0.0'
__name__ = 'gps'
__license__ = 'GPL3'
__description__ = 'Save GPS coordinates whenever a handshake is captured.'

import logging
import json
import os

running = False
OPTIONS = dict()


def on_loaded():
    logging.info("gps plugin loaded for %s:%d" % OPTIONS['gpsdHost'], OPTIONS['gpsdPort'])


def on_ready(agent):
    global running

    logging.info("enabling gps bettercap's module for %s:%d" % OPTIONS['gpsdHost'], OPTIONS['gpsdPort'])
    try:
        agent.run('gps off')
    except:
        pass

    agent.run('set gps.gpsdHost %s' % OPTIONS['gpsdHost'])
    agent.run('set gps.gpsdPort %d' % OPTIONS['gpsdPort'])
    agent.run('gps on')
    running = True


def on_handshake(agent, filename, access_point, client_station):
    if running:
        info = agent.session()
        gps = info['gps']
        gps_filename = filename.replace('.pcap', '.gps.json')

        logging.info("saving GPS to %s (%s)" % (gps_filename, gps))
        with open(gps_filename, 'w+t') as fp:
            json.dump(gps, fp)
