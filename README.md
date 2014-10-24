sound-sync
==========

These three little python programs **server.py**, **clientListen.py** (or **clientListenWindow.py** for a not-nice GUI) 
and **clientSender.py** implement a messaging protocol to listen to the same audio in real time and synced.

running the programs
--------------------

You will need python2.7 and the python package *python-alsaaudio*. And *python-tk* for running the GUI.

We need a minimum of three programs to implement this messaging protocol. The needed config options can be set in 
`/etc/sound-sync.conf`. A default file can be found under `sound-sync.conf` in this repository.

* First we need a server to handle all the requests. For this run **server.py** on a computer of your 
choice. For me even a Raspberry Pi does the job perfectly well. Change the ip address in **clientBase.py** accordingly!
* Then we need a client to send the audio data to the server. Thi sender can run on any computer you like. 
This is implemented in **clientSender.py**. It collects the audio data from your ALSA loopback adapter. If you do not 
have one, start it by loading the corresponding alsa-module (search in the internet if you do not know how. A starting 
point would be `modprobe snd-aloop` or adding snd-aloop to /etc/modules or a file in /etc/modules.d/). 
To send the data from other programs (like your favourite music player or your web browser) use gstreamer, pulseaudio or
jack - dependent on your audio server. For pulseaudio for example open pavucontrol and send the audio output from the apps 
to Alsa Loopback.
* Then we need as many listeners as you like. Start **clientListener.py** for a terminal application of 
**clientListenerWindow.py** for a small GUI to start the listener on any computer. It connects to the server (have you 
changed the ip accordingly in **clientBase.py**?) and starts playing to the default alsa device. If you do not know which 
device this is you probably do not have to worry about that.

Everything should run fine than. A short pause in the beginning is normal. The listener "reboots" automatically 
after 10 minutes. There will be a short break while playing. This is needed to resync again.

how it works
------------

Have a look at the code to see how it works.
TODO

ToDo
----
* Implement better error handling for server
* Implement more than one client

