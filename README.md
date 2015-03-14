sound-sync
==========

Many computer setup at home include more than one computer nowadays - like laptops, smartphones, raspberries etc. With small effort it is possible to access all the media from all computers, for example by running a raspberry as a NAS. 
But for a real multimedia home setup one feature lacks: to play the same music in the same time on every machine without glitches, pauses... 
There are some possibilities:
* Storing the music on a central archive (like a NAS) and accessing it from every computer. Then pressing start at exactly the same time (as this can not be done by hand you can write a script easily by using ssh or another protocol). This approuch is probably the "easiest" one but leads to some issues because every single device and every single music player has a distinct starting time. Also this approach is only possible for real music files - not for streams like youtube, spotify etc.
* Using something like the real-time transport protocol from pulseaudio (see [here][http://www.linux.com/learn/tutorials/332418:weekend-project-using-pulseaudio-to-share-sound-across-all-your-computers]). With this setup you can stream all sorts of media from every device running pulseaudio to every other device running pulseaudio (no chance for smartphones and raspberries). The problem with this approach is the reoccuring glitches (at least in my network setup).
* Or you use these little scripts here. These three little programs **server** (find it in server/Server), **clientListen.py** (or **clientListenWindow.py** for a not-nice GUI) and **clientSender.py** implement a messaging protocol to listen to the same audio in real time and synced without pauses or glitches. They run on every linux device with alsa and python installed. I plan to implement an android app too.


Requirements
-----------

For the two python scripts you will need python2.7 and the python package *python-alsaaudio*. And *python-tk* for running the GUI.
For compiling the C++ programm **server** you will need the library *pugixml* (see http://pugixml.org/). As the tests in server/tests rely on the google testing framework, you will also need the headers and libs for that (remember to install them probably if using ubuntu: [see here](http://askubuntu.com/questions/145887/why-no-library-files-installed-for-google-test))


running the programm
------------------------------------

You need three computers to act as the three parts: the server, the sender, the listener (this is not exactly correct: the three parts yan be played by single computer also and you can have as many listener as you like. But we keep it simple here).
* On the server download the files from the git repository, compile the C++ application in server and the tests and run the tests and the application
```
git clone https://github.com/nilpferd1991/sound-sync
cd sound-sync/server/tests
make
./test
cd ..
make
./Server/server
```
For compilation you will need *pugixml* and for the tests the google testing framework.
* On the sender download the files, copy the settings file and change the settings accordingly. Then start the listener and send data to the server
```
git clone https://github.com/nilpferd1991/sound-sync
cd sound-sync/server
vim sound-sync.conf		# Change the ip to the ip address of the server. Leave the rest as it is.
cp sound-sync.conf /etc/sound-sync.conf # You may need root for this
./clientSender.py
```
For sending the sound data to the server start your favourite music player (something like totem or your browser for youtube or spotify). Then send the music data to the Alsa Loopback Adapter. To start the loopback adapter (if you do not have one) load the kernel module snd-aloop with `modprobe snd-aloop`.
For example you can use pulseaudio:
pavucontrol -> first tab -> search for the music playing program -> click on the button on the right and choose Also Looback.
Or gstreamer by changing the gstreamer-properties to use the loopback from alsa.
Or jack.
Or your .asoundrc to send all data to the loopback.

* On the listener download the files, copy the settings file and change the settings accordingly (see above). Then start the listener and enjoy.
```
git clone https://github.com/nilpferd1991/sound-sync
cd sound-sync/server
vim sound-sync.conf		# Change the ip to the ip address of the server. Leave the rest as it is.
cp sound-sync.conf /etc/sound-sync.conf # You may need root for this
./clientListen.py # or ./clientListenWindow.py
```

Notes
-----

* The needed config options can be set in */etc/sound-sync.conf*. A default file can be found under *sound-sync.conf* in this repository. In the moment, the server uses no settings file - so the port is set to 50007 all the time. The entries for the sound settings (like channels, frame_rate etc.) should be good in most of the cases. Do not change them (also, not all of them are implemented correctly).
* You can use every device you like: laptop, computer, raspberry, tablet. As long as it runs some sort of linux. For the server, wo do not need audio.
* You can listen to your own music while sending by executing **clientListen.py** on the same computer.
* To load the alsa loopback module you can use `modprobe snd-aloop` or add to */etc/modules*. Search the internet if you do not know how.
* A short pause in the beginning is normal. During this uptime, the client syncs with the sender. 
* The listener "reboots" automatically after 10 minutes. There will be a short break while playing. This is needed to resync again.

how it works
------------

Have a look at the code to see how it works :-)
