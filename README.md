# pwnagotchi_plugins
Pwnagotchi Plugins and Things for Mayhem and Profit

I don't know if I really like this pwnagotchi project. It's useful because it really does provide a smarter wireless access point pen-testing/surveilance wrap around bettercap, that I can actually take to an engagement, walk around, and not automatically create mass panic and a huge fucking mess dauthing every living thing at the exact same time. I also see great potential for distributed mesh networking research and exploring ideas of post-apocalyptic networking and covert information sharing. On the other hand, the pwnagotchi subReddit and overall goal of the pwnagotchi project makes it seem like an absolute public nuisance and threat to workplace productivity. Most people have no idea what they're doing; they just want something fun that says 'pwn' on it and want to be part of a community. I don't want to say the neural networking portion is pointless; it's fun, but not the optimal solution for finding the right variables to capture handshakes with. Also, I don't think capturing handshakes really qualifies as a 'pwn' - it's not pwnt until you've broken the law and you're inside (/sarcasm).

Please don't break the law and/or use anything here to break the law. Laws vary, depending on location, so always be aware of what you're doing and where you're doing it. 

## quick_rides_to_jail.py
Almost certainly illegal, wherever you are, if not used for research purposes against your own equipment. It replaces quickdic.py, completing the pwn process by adding any cracked access points to wpa_supplicant's config (by BSSID) and restarting wpa_supplicant for the hardcoded interface, enabling automatic authentication when in range of a pwnd AP. This was the easiest solution I could come up with for authenticating to a wireless network, with cracked creds, when the network is in range. Managing all of that in one Python script would be a terrible multithreaded mess that would probably end up fighting against most OS's network management services for dominance. I wrote this in a mostly-default Raspbian build, on both a Raspi 3b+ and 4, and I can't remember if the pwnagotchi image has wpa_supplicant and some network manager running. One also needs a separate wireless interface if one expects to connect to pwnt AP's while still running the pwnagotchi. Since you're only using this on your own test infrastructure, you shouldn't have to worry about any malicious threats once you've authenticated to and joined your pwnt test infrastructure. Also not meant for skiddies.

## monstart/monstop
Not mine, but also don't remember where I got them. Pretty sure they came from one of evilsocket's repo's or something they used to create their build environment. As their names imply, these scripts are used to start and stop an interface in monitor mode. The interface these scripts perform the operations on is hardcoded in each script. The interface name currently in both scripts should be changed to the name you want your monitor mode interface to have, based off an existing interface (e.g. wlan1mon because I have a wlan1). Added because I'm using raspbian and built everything, myself. 

## gsmfake
Real shitty hacks to use the [Waveshare Raspberry Pi GSM/GPRS/GNSS Bluetooth Hat for SIM868](https://amazon.com/Raspberry-Bluetooth-Expansion-Compatible-DataTransfer/dp/B076CPX4NN) with gpsfake, to supply bettercap with better-than-nothing GPS coordinates from the GSM network. Use when stuck in and around glass/steel monoliths that eat GPS signals for breakfast. The provided coordinates are not only inaccurate because they come from second-hand means, but also because said means don't return elevation, so I put a hardcoded 100 in there because I don't know why. Really, I should focus on a more accurate 2d-fix over the 3d-fix, but I didn't. Requires the python gps modules (pip install gps) and pynmea2 for creating nice NMEA strings (pip install pynmea2). Make a backup of '/usr/lib/python2.7/dist-packages/gps/fake.py' and then replace it with the one provided (not totally necessary). Then run 'prime_gsm_hat.py' to turn on the hat and start the GPRS data service. This only needs to be/should be run once per powering on of the hat. Next, run gsmfake.py using basic parameters used to start gpsfake: 'gsmfake -t -P 2947 /root/fakegps.data'. Both fake.py and prime_gsm_hat.py have hardcoded paths to the Hat's serial IO, so keep that in mind.

I *think* everything is in a working state, but good luck if it's not. There are very few checks done and errors handled, so everything needs to work 100% perfect to get it running. Once it is running, gsmfake should spit out a special file path. Copy and paste this into bettercap's advanced GPS settings for or directly set 'gps.device' and restart the gps caplet.

TODO: Figure out how to coalesce multiple GPS sources into a more accurate location, figure out how to replace 3d-fixes with 2d-fixes, and fix the Wiggle plugin, because that shit aint right.

## notes_on_pwnagotchi_on_other_pis_and_raspbian.txt
Notes on how I got things running on Pi 3 b+/Pi 4/Raspbian etc.


#### Coming soon
* Comms over GSM/GPRS
* Modifications to the Wiggle plugin
* That WPS shit everyone keeps talking about
* OpenVPN and then TOR support for plugins/pieces that touch the internet.
