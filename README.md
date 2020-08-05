# Call Attendant
Automated call attendant with call blocking and voice messaging on a Raspberry Pi.

#### Table of Contents
- [Overview](#overview)
- [Software Architecture](#software-architecture)
- [Software Development Plan](#software-development-plan)
- [Installation](#installation)
- [Operation](#operation)
- [Related Projects](#related-projects)


## Overview
The Call Attendant (__callattendant__) is a python-based, automated call attendant that runs on a lightweight Raspberry Pi
or other Linux-based system. Coupled with a modem, it provides a call blocker and voice messaging system that can screen
callers and block robocall and scams from your landline.

Features being developed include:
- [x] A call blocker that intercepts robocallers and blocked numbers at or before the first ring
- [x] Permitted numbers pass straight through to the local phone system for normal call ringing and answering
- [x] Visual indicators to show whether the incoming call is from a permitted, blocked, or unknown number
- [x] Call details, permitted numbers, and blocked numbers are available in a web-based user interface
- [ ] Blocked callers are handled by a voice messaging system that requires human interaction, e.g, "Press 1 to leave a message"

### Hardware
- Raspberry Pi 3B+ or better
- US Robotics 5637 Modem

##### _The required hardware components: a Raspberry Pi 3B+ and USR5637 modem_
![Raspberry Pi and USR5637 Modem](https://github.com/emxsys/callattendant/raw/master/docs/raspberry_pi-modem.jpg)

### Web Interface
Call history, permitted numbers, blocked numbers and caller management is all performed through a web interface.

##### _Call Log Example_
![Call Log](https://github.com/emxsys/callattendant/raw/master/docs/callattendant-calllog.png)

### More information
The Call Attendant project was inspired by the [pamapa/callblocker](https://github.com/pamapa/callblocker) project,
an excellent Raspberry Pi based call blocker.  However, the __callattendant__ differs from the __callblocker__ in that adds
voice messaging; and the __callattendant__ is written entirely in Python, uses SQLite for the call logging, and
implments the web interface with Flask.

The following blogs from [IoT Bytes by Pradeep Singh](https://iotbytes.wordpress.com/) were very useful for learning to how
to program the Raspberry Pi and the US Robotics 5637 modem. His blog site has many Raspberry Pi resources. Thanks Pradeep!

- [Incoming Call Details Logger with Raspberry Pi](https://iotbytes.wordpress.com/incoming-call-details-logger-with-raspberry-pi/)
- [Play Audio File on Phone Line with Raspberry Pi](https://iotbytes.wordpress.com/play-audio-file-on-phone-line-with-raspberry-pi/)
- [Record Audio from Phone Line with Raspberry Pi](https://iotbytes.wordpress.com/record-audio-from-phone-line-with-raspberry-pi/)



## Software Architecture
### Archtectural Viewpoints
###### _Rational Unified Process 4+1 View_
![Alt text](https://github.com/emxsys/callattendant/blob/master/docs/images/RUP_41_View.png "RUP 4+1 View")

### Use Case View
###### _Use Case Diagram_
![Alt text](https://github.com/emxsys/callattendant/blob/master/docs/images/Use_Case_View.png "Use Case Diagram")

### Logical View
###### _Class Diagram_
![Alt text](https://github.com/emxsys/callattendant/blob/master/docs/images/Logical_View.png "Logical View Diagram")

### Process View
###### _Activity Diagram_
![Alt text](https://github.com/emxsys/callattendant/blob/master/docs/images/Process_View.png "Process View Diagram")

###### _Sequence Diagram_
![Alt text](https://github.com/emxsys/callattendant/blob/master/docs/images/Main_Sequence_Diagram.png "Main Sequence Diagram")

### Implementation View
###### _Component Diagram_
![Alt text](https://github.com/emxsys/callattendant/blob/master/docs/images/Implementation_View.png "Implementation Diagram")

### Deployment View
###### _Deployment Diagram_
![Alt text](https://github.com/emxsys/callattendant/blob/master/docs/images/Deployment_View.png "Deployment Diagram")

### Data View
###### _Entity Relationship Diagram_
![Alt text](https://github.com/emxsys/callattendant/blob/master/docs/images/Data_View.png "Entity Relationship Diagram")

---

## Software Development Plan
The development plan's [phase objectives](https://github.com/emxsys/callattendant/projects?query=is%3Aopen+sort%3Acreated-asc) are captured in the GitHub projects.
### [Inception Phase](https://github.com/emxsys/callattendant/projects/1)
- Iteration #I1: [v0.1](https://github.com/emxsys/callattendant/releases/tag/v0.1)
### [Elaboration Phase](https://github.com/emxsys/callattendant/projects/2)
- Iteration #E1: [v0.2](https://github.com/emxsys/callattendant/releases/tag/v0.2)
### [Construction Phase](https://github.com/emxsys/callattendant/projects/3)
- Iteration #C1: [v0.3](https://github.com/emxsys/callattendant/issues?q=is%3Aopen+is%3Aissue+milestone%3A%22Release+0.3%22)
- Iteration #C2: [v0.4](https://github.com/emxsys/callattendant/issues?q=is%3Aopen+is%3Aissue+milestone%3A%22Release+0.4%22)
### [Transition Phase](https://github.com/emxsys/callattendant/projects/4)
- Iteration #T1: [v1.0](https://github.com/emxsys/callattendant/issues?q=is%3Aopen+is%3Aissue+milestone%3A%22Release+1.0%22)

---

## Installation

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

### Run as a Service
###### *Optional*
We're going to define a service to automatically run the Call Attendant on the Raspberry Pi at start up. Our simple service will run the `callattendant.py` script and if by any means is aborted it is going to be restarted automatically.

#### Create the Service

##### Step 1. Create the Unit File
The service definition must be on the `/lib/systemd/system` folder. Our service is going to be called "callattendant.service":

```Shell
cd /lib/systemd/system/
sudo nano callattendant.service
```

Copy the following text into the `callattendant.service` unit file, using your path to `callattendant.py`:

```text
[Unit]
Description=Call Attendant
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python /home/pi/callattendant/src/callattendant.py
WorkingDirectory=/home/pi/callattendant/src
Restart=on-abort

[Install]
WantedBy=multi-user.target
```
You can check more on service's options in the next wiki: https://wiki.archlinux.org/index.php/systemd.

##### Step 2. Activate the Service
Now that we have our service we need to activate it:

```Shell
sudo chmod 644 /lib/systemd/system/callattendant.service
chmod +x /home/pi/callattendant/src/callattendant.py
sudo systemctl daemon-reload
sudo systemctl enable callattendant.service
sudo systemctl start callattendant.service
```

#### Service Tasks
For every change that we do on the `/lib/systemd/system` folder we need to execute a
`daemon-reload` (third line of previous code).

You can execute the following commands as needed to check the status, start and stop
the service, or check the logs. Several shell scripts are included in the root of this
project to perfom these tasks.

##### Check status
`sudo systemctl status callattendant.service`

##### Start service
`sudo systemctl start callattendant.service`

##### Stop service
`sudo systemctl stop callattendant.service`

##### Check service's log
`sudo journalctl -f -u callattendant.service`

---

## Operation

### Web Pages
A few web pages are used to monitor your installation. You can use `localhost` for the `pi_address`
when you are running the web browser on the pi.

##### Call Log
The call log displays all the calls that have been processed by the call attendant. This list refreshes
automatically after a period of several minutes.
```
http://localhost:5000/
```
##### Blocked List
This is the list of blocked numbers.
```
http://localhost:5000/blocked
```

##### Permitted List
This is the list of permitted numbers.
```
http://localhost:5000/permitted
```
### Tools

#### DB Browser for SQLite
If needed, you can use **DB Browser for SQLite** to view and edit the tables used by the **callattendant**.

```
sudo apt-get install sqlitebrowser
```
```
sqlitebrowser callattendant/src/callattendant.db
```

---

## Related Projects

- [pamapa/callblocker](https://github.com/pamapa/callblocker)
- [pradeesi/Incoming_Call_Detail_Logger ](https://github.com/pradeesi/Incoming_Call_Detail_Logger)
- [pradeesi/record_audio_from_phone_line](https://github.com/pradeesi/record_audio_from_phone_line)
- [pradeesi/play_audio_over_phone_line](https://github.com/pradeesi/play_audio_over_phone_line)

