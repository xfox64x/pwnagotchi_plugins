# pwnagotchi_plugins
Pwnagotchi Plugins and Things for Mayhem and Profit

Please don't break the law and/or use anything here to break the law. Laws vary, depending on location, so always be aware of what you're doing and where you're doing it. 

## quick_rides_to_jail/*
Almost certainly illegal, wherever you are, if not used for research purposes against your own equipment. It replaces quickdic.py, completing the pwn process by adding any cracked access points to wpa_supplicant's config (by BSSID) and restarting wpa_supplicant for the hardcoded interface, enabling automatic authentication when in range of a pwnd AP. This was the easiest solution I could come up with for authenticating to a wireless network, with cracked creds, when the network is in range. Managing all of that in one Python script would be a terrible multithreaded mess that would probably end up fighting against most OS's network management services for dominance. I wrote this in a mostly-default Raspbian build, on both a Raspi 3b+ and 4, and I can't remember if the pwnagotchi image has wpa_supplicant and some network manager running. One also needs a separate wireless interface if one expects to connect to pwnt AP's while still running the pwnagotchi. Since you're only using this on your own test infrastructure, you shouldn't have to worry about any malicious threats once you've authenticated to and joined your pwnt test infrastructure. Also not meant for skiddies.

Now includes logic to re-crack uncracked captures, since the original plugin would only initiate cracking once, immediately after discovery. In a similar fashion to the Wigle plugin, I've added a status file (`/root/.aircracked_pcaps`) so that we aren't trying to crack the same things over and over. The aircrack-ng command is limited to 1 cpu core, to prevent the Pi from melting. I recommend using a small wordlist, of the most common passwords, so that cracking doesn't hold up normal operations too long. I also added more robust aircrack logic, so we start cracking pcap's that only contain PMKID and/or multiple handshakes (which would fail using the default plugin). I guess I'll remove the sketchy stuff and create a separate quickdic.py plugin...

## quickdic/*
A better quickdic, with less quick rides to jail. I just removed the quick_rides part so you don't accidently jail. Does the same Aircrack-ng logic. Completely untested.

## wigle.py
It's the WiGLE module, but it actually works. It now combines all data into one Kismet CSV file, before uploading to WiGLE. I'm hoping to improve it, in the future, by adding logic to report all AP's, not just those with handshakes, and by adding support for other device information WiGLE can consume. Pull request denied, so this lives here now - there's more to life than fake internet points for free work. The original Wigle plugin isn't formatted correctly to work as a plugin; it's different from all of the other plugins because, I guess, it's still a work in progress. Meh. This one works and isn't cancer.

## monstart/monstop
Not mine, but also don't remember where I got them. Pretty sure they came from one of evilsocket's repo's or something they used to create their build environment. As their names imply, these scripts are used to start and stop an interface in monitor mode. The interface these scripts perform the operations on is hardcoded in each script. The interface name currently in both scripts should be changed to the name you want your monitor mode interface to have, based off an existing interface (e.g. wlan1mon because I have a wlan1). Added because I'm using raspbian and built everything, myself. 

## gsmfake
Real shitty hacks to use the [Waveshare Raspberry Pi GSM/GPRS/GNSS Bluetooth Hat for SIM868](https://amazon.com/Raspberry-Bluetooth-Expansion-Compatible-DataTransfer/dp/B076CPX4NN) with gpsfake, to supply bettercap with better-than-nothing GPS coordinates from the GSM network. Use when stuck in and around glass/steel monoliths that eat GPS signals for breakfast. The provided coordinates are not only inaccurate because they come from second-hand means, but also because said means don't return elevation, so I put a hardcoded 100 in there because I don't know why. Really, I should focus on a more accurate 2d-fix over the 3d-fix, but I didn't. Requires the python gps modules (pip install gps) and pynmea2 for creating nice NMEA strings (pip install pynmea2). Make a backup of '/usr/lib/python2.7/dist-packages/gps/fake.py' and then replace it with the one provided (not totally necessary). Then run 'python prime_gsm_hat.py' to turn on the hat and start the GPRS data service. This only needs to be/should be run once per powering on of the hat. Next, run gsmfake.py using basic parameters used to start gpsfake: 'python gsmfake.py -P 2948 /root/fakegps.data'. Both fake.py and prime_gsm_hat.py have hardcoded paths to the Hat's serial IO, so keep that in mind. This will spit out a path like '/dev/pts/2' that you need to update bettercap with.

I *think* everything is in a working state, but good luck if it's not. There are very few checks done and errors handled, so everything needs to work 100% perfect to get it running. Once it is running, gsmfake should spit out a special file path. Copy and paste this into bettercap's advanced GPS settings for or directly set 'gps.device' and restart the gps caplet.

TODO: Figure out how to coalesce multiple GPS sources into a more accurate location, figure out how to replace 3d-fixes with 2d-fixes, and fix the Wiggle plugin, because that shit aint right.

## notes_on_pwnagotchi_on_other_pis_and_raspbian.txt
Notes on how I got things running on Pi 3 b+/Pi 4/Raspbian etc.

## gps/*
Replacements for bettercap's gps.go and pwnagotchi's gps.py to get it working with gpsd, for a more robust, multiplexed GPS experience. Bettercap will get GPS updates by polling gpsd, allowing other processes access to the GPS data; not just bettercap. Requires that you have gpsd installed and configured, as well as [Stratoberry's go-gpsd](github.com/stratoberry/go-gpsd). So install and configure gpsd, replace your `~/go/src/github.com/bettercap/bettercap/modules/gps/gps.go` with the Go script, replace `~/git/pwnagotchi-1.0.1/pwnagotchi/plugins/default/gps.py` with the Python script, modify your pwnagotchi config with the included config, change back to the bettercap directory, do a little `make build`, and replace your bettercap binary with the one you just built.

There's no clear benefit to using more than one GPS device, beyond testing antenna/signal strength (your receivers aren't magically more accurate). 

## event_multithreading_for_plugins/*
I've added logic to multithread and queue events for plugins. It's been noted that the way pwnagotchi handles tasking events on the plugins causes everything to slow, depending on the collective speed of the plugins, because they were being processed serially. The `pwnagotchi/plugins/__init__.py` has been updated to create a thread-managed queue for each event type, for each plugin. When an event is processed on all plugins containing a function definition for the event, it gets added to the back of a queue for processing that specific type of event on a valid plugin, and then the thread will take care of executing the events in the order they came in. Moving forward, this should have little, if any, impact on my future development efforts because I fully expect evilsocket to put out their own multithreaded version soon, but I can't be bothered to follow arbitrary style guides for free. However, I'm not sure this will work on any future evilsocket pwnagotchi releases because I cannot predict what they will do. My pwnagotchi fork should contain all of the fixes/plugins/etc. here; I'll consider being an asshole in the future.  

#### Coming soon
* Comms over GSM/GPRS
* That WPS shit everyone keeps talking about
* OpenVPN and then TOR support for plugins/pieces that touch the internet.
