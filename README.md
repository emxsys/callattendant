# Call Attendant
Automated call attendant with call blocking and voice messaging running on a Raspberry Pi. Stop annoying robocalls and spammers
from interrupting your life.

_If you're at all interested in this project, please provide some feedback by giving it a [star](https://github.com/emxsys/callattendant/stargazers), 
or even better, get involved by filing [issues](https://github.com/emxsys/callattendant/issues) or [pull requests](https://github.com/emxsys/callattendant/pulls)._

#### Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [More Information](#more-information)


## Overview
The Call Attendant (__callattendant__) is a python-based, automated call attendant that runs on a lightweight Raspberry Pi
or other Linux-based system. Coupled with a modem, it provides a call blocker and voice messaging system that can screen
callers and block robocall and scams from your landline.

Features include:
- [x] A call blocker that intercepts robocallers and blocked numbers at or before the first ring
- [x] Permitted numbers pass straight through to the local phone system for normal call ringing and answering
- [x] Visual indicators to show whether the incoming call is from a permitted, blocked, or unknown number
- [x] Call details, permitted numbers, and blocked numbers are available in a web-based user interface
- [x] Blocked callers are handled by a voice messaging system that requires human interaction, e.g, "Press 1 to leave a message"

### Hardware
The __callattendant__ uses the following hardware:
- Raspberry Pi 3B+ or better
- US Robotics 5637 Modem

For a complete description of the hardware setup see the [Installation](https://github.com/emxsys/callattendant/wiki/Home#installation) 
section of the [Wiki](https://github.com/emxsys/callattendant/wiki/Home).

##### _The required hardware components: a Raspberry Pi 3B+ and USR5637 modem_
![Raspberry Pi and USR5637 Modem](https://github.com/emxsys/callattendant/raw/master/docs/raspberry_pi-modem.jpg)

### Web Interface
Call history, playing voice messages, permitted numbers, blocked numbers and caller management is performed through the Call Attendant's web interface.
Following is an example of the main screen, the Dashboard, including metrics and a list of recent calls.  
For a complete description see the [User Guide](https://github.com/emxsys/callattendant/wiki/User-Guide).

##### _Dashboard/home page as seen on an IPad Pro and a Pixel 2 phone_
![Dashboard - Responsive](https://github.com/emxsys/callattendant/blob/master/docs/dashboard-responsive.png)

### Setup
See the [Call Attendant Wiki](https://github.com/emxsys/callattendant/wiki/Home) for complete installation, configuration, and operation instructions.   

### User Guide
See the [User Guide](https://github.com/emxsys/callattendant/wiki/User-Guide) in the project's wiki for web interface instructions.  

### Developer Guide
The [Wiki](https://github.com/emxsys/callattendant/wiki) includes a [Developer Guide](https://github.com/emxsys/callattendant/wiki/Developer-Guide) 
that describes the software architecture and software development plan.

### More Information
The [Wiki](https://github.com/emxsys/callattendant/wiki) has an [Advanced](https://github.com/emxsys/callattendant/wiki/Advanced) page for 
more complex setups and situations. For instance, _running as a service_.

---

## Quick Start

### Prequisites
#### Hardware

You will need a Raspberry Pi running Raspbian or better and access to the Internet 
for the software installation. For the project, you will need a modem of some sort to
do the telephony communications.

The **U.S. Robotics USR5637 56K USB Modem**:

https://www.amazon.com/gp/product/B0013FDLM0/ref=ppx_yo_dt_b_asin_image_o03_s00?ie=UTF8&psc=1

has been proven effective. For some installs, it just works, no config needed.
It showed up as /dev/ttyACM0.

#### Software

You need a copy of this repository placed in a folder on your pi, e.g., `/pi/home/callattendant`.
You can either clone this repository, or [download a zip file](https://github.com/emxsys/callattendant/archive/master.zip),
or download a specific release from [Releases](https://github.com/emxsys/callattendant/releases).

##### Clone wtih Git

Here's how clone the repository with `git` into your home folder:

```bash
cd 
git clone https://github.com/emxsys/callattendant.git
cd callattendant
```

##### Download Zip

If you [download the latest code](https://github.com/emxsys/callattendant/archive/master.zip) or a
specific release, the unzpped folder will be named `callattendant-master` or `callattendant-<release_tag>` 
depending on what you downloaded. You can rename it if you wish. Here's how unzip it into your home folder.

```bash
cd
unzip ~/Downloads/callattendant-master.zip 
cd callattendant-master
```

### Setup

The installation calls for Python3.X.

#### Setup Virtual Environment
###### *Optional*

For development purposes, you might be best served by setting up a virtual environment.
If you intend to simply install and run the **callattendant** on a dedicated Raspberry Pi, 
you can skip this step and proceed with [Install Packages](#install-packages).

The following instructions create a virtual environment named _python3_ within the current
folder:

```bash
sudo apt install virtualenv

virtualenv python3 --python=python3

source python3/bin/activate
```

Now you're operating with a virtual Python. To check, issue the following
command:

```bash

$ which python
```

You should see output of the form:

```
(python3) pi@raspberryi:~/testing $ which python
/home/pi/testing/python3/bin/python
```

To make sure you're on 3.x as requested, issue:

```bash

$ python --version
```

You should see output of the form:

```
(python3) pi@raspberrypi:~/testing $ python --version
Python 3.7.3
```

#### Install Packages

We've provided a requirements file called `requirements.txt`. Let's use it to
install the required packages. But first, navigate to the folder where the 
callattendant repository was placed, e.g., `/pi/home/callattendant`.

```bash
$ pip install -r requirements.txt
```

In my install, lxml took a long time to build (because Raspberry Pi) but it's
worth the wait to get to that part of blocking spam calls. So chill and do
whatever it is you do while software builds.

### Initialization

In the `callattendant/src` directory, issue the following command:

```bash
python callattendant.py
```

You should see output of the form:

```
(python3) pi@raspberrypi:~/testing/callattendant/src $ python callattendant.py
CallLogger initialized
Blacklist initialized
Whitelist initialized
AT+FCLASS=8
OK
Modem COM Port is: /dev/ttyACM0
AT
OK
ATZ3
OK
ATV1
OK
ATE1
OK
AT+VCID=1
OK
ATI4
 * Serving Flask app "userinterface.webapp" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 ----Option----- --Setting-- Cmd  ----Option----- --Setting-- --Cmd--
 Comm Standard   CCITT       B0   Answer Ring#    0            S0=000
 Command Echo    Enabled     E1   Escape Char     43           S2=043
 Speaker Volume  Medium      L2   CR Char         13           S3=013
 Speaker Control OnUntilCD   M1   LF Char         10           S4=010
 Result Codes    Enabled     Q0   BS Char         8            S5=008
 Dialer Type     Tone        T/P  Dial Pause      3 sec        S6=003
 Result Form     Text        V1   NoAns Timeout   60 sec       S7=060
 Extend Result   Enabled     X4   "," Pause       2 sec        S8=002
 DialTone Detect Disabled    X4   No CD Disc      2000 msec   S10=020
 BusyTone Detect Disabled    X4   DTMF Speed      95 msec     S11=095
 DCD Action      Std RS232   &C1  Esc GuardTime   1000 msec   S12=050
 DTR Action      Std RS232   &D2  Calling Tone    Enabled     S35=001
 V22b Guard Tone Disabled    &G0  Line Rate       33600       S37=000
 Flow Control    Disabled    &H0
 Error Control   V42,MNP,Bfr &M4
 Compression     44 42b MNP5 &K1
OK
```

Navigate to <pi_address> on port 5000 and you should see the home page. Make a few calls to
yourself to test the service.

---
### Configuration
The Call Attendant's behavior can be controlled by a configuration file. To override the default configuration, 
copy the `src/app.cfg.example` file to a new file, e.g. `src/app.cfg` and edit its contents. Use an editor that 
provides Python syntax highlighting, like nano. Then use your configuration file when starting the callattendant.

Specify the configuration file on the command line, e.g.:
```
python3 src/callattendant.py --config app.cfg
```
See the [Configuration](https://github.com/emxsys/callattendant/wiki/Home#configuration) section in the project's 
wiki for more information. 

---

### Web Interface
#### URL: http://<pi-address>|<pi-hostname>:5000
To view the web interface, simply point your web browser to port `5000` on your Raspberry Pi. I
For example, in your Raspberry Pi's browser, you can use:
```
http://localhost:5000/
```

---

## More information
The Call Attendant project was inspired by the [pamapa/callblocker](https://github.com/pamapa/callblocker) project,
an excellent Raspberry Pi based call blocker.  However, the __callattendant__ differs from the __callblocker__ in that adds
voice messaging; and the __callattendant__ is written entirely in Python, uses SQLite for the call logging, and
implments the web interface with Flask.

The following blogs from [IoT Bytes by Pradeep Singh](https://iotbytes.wordpress.com/) were very useful for learning to how
to program the Raspberry Pi and the US Robotics 5637 modem. His blog site has many Raspberry Pi resources. Thanks Pradeep!

- [Incoming Call Details Logger with Raspberry Pi](https://iotbytes.wordpress.com/incoming-call-details-logger-with-raspberry-pi/)
- [Play Audio File on Phone Line with Raspberry Pi](https://iotbytes.wordpress.com/play-audio-file-on-phone-line-with-raspberry-pi/)
- [Record Audio from Phone Line with Raspberry Pi](https://iotbytes.wordpress.com/record-audio-from-phone-line-with-raspberry-pi/)

