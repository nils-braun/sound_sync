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


running the programm - the short way
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


running the program - the long way
----------------------------------


We need a minimum of three programs to implement this messaging protocol. The needed config options can be set in 
*/etc/sound-sync.conf*. A default file can be found under *sound-sync.conf* in this repository.

* First we need a server to handle all the requests. For this run **server** on a computer of your 
choice. For me even a Raspberry Pi does the job perfectly well. Please change the ip address in */etc/sound-sync.conf* accordingly!
* Then we need a client to send the audio data to the server. This sender can run on any computer you like. 
It is implemented in **clientSender.py**. The script collects the audio data from your ALSA loopback adapter. If you do not 
have one, start it by loading the corresponding alsa-module (search the internet if you do not know how. A starting 
point would be `modprobe snd-aloop` or adding snd-aloop to */etc/modules* or a file in */etc/modules.d/*). 
To send the data from other programs (like your favourite music player or your web browser) use gstreamer, pulseaudio or
jack - dependent on your audio server. For pulseaudio for example open **pavucontrol** and send the audio output from the apps 
to Alsa Loopback.
* Then we need as many listeners as you like. Start **clientListener.py** for a terminal application or 
**clientListenerWindow.py** for a small GUI to start the listener on any computer. It connects to the server (have you 
changed the ip accordingly in */etc/sound-sync.conf*?) and starts playing to the default alsa device. If you do not know which 
device this is, you probably do not have to worry about that.

Everything should run fine now. A short pause in the beginning is normal. The listener "reboots" automatically 
after 10 minutes. There will be a short break while playing. This is needed to resync again.

how it works
------------

Have a look at the code to see how it works :-)
