# Call Attendant
Automated call attendant, call blocker, and voice messaging on a Raspberry Pi.

#### Table of Contents
- [Overview](#overview)
- [Software Architecture](#software-architecture)
- [Software Development Plan](#software-development-plan)
- [Installation](#installation)

## Overview
The Call Attendant (__callattendant__) uses a Raspberry Pi coupled with a US Robotics 5637 modem to screen incoming 
calls on a landline. Features being developed include:
- [x] Robocallers and blacklisted numbers are intercepted after the first ring
- [x] Whitelisted callers pass straight through to the local phone system for normal call ringing and answering
- [x] Visual indicators to show whether the incoming call is from a whitelisted, blacklisted, or unknown number 
- [ ] Unknown callers are handled by a voice messaging system that requires human interaction, e.g, "Press 1 to leave a message"
- [ ] Call details, blacklists, whitelists are available in a web-based user interface 

The Call Attendant project was inspired by the [pamapa/callblocker](https://github.com/pamapa/callblocker) project,
an excellent Raspberry Pi based call blocker.  However, the __callattendant__ differs from the __callblocker__ in that adds
voice messaging; and the __callattendant__ is written entirely in Python, uses SQLite for the call logging, and
implments the web interface with Flask. 

### Context Diagrams
###### System View
![Alt text](https://github.com/emxsys/callattendant/blob/master/docs/images/System_View.png "System View")

###### _Subsystem View_
![Alt text](https://github.com/emxsys/callattendant/blob/master/docs/images/Subsystem_View.png "Subsystem View")

### More information
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
###### _Main Use Case Diagram_
![Alt text](https://github.com/emxsys/callattendant/blob/master/docs/images/Main_Use_Case_Diagram.png "Main Use Case Diagram")

### Logical View
###### _Main Class Diagram_
![Alt text](https://github.com/emxsys/callattendant/blob/master/docs/images/Main_Class_Diagram.png "Main Class Diagram")

### Process View
###### _Main Activity Diagram_
![Alt text](https://github.com/emxsys/callattendant/blob/master/docs/images/Main_Activity_Diagram.png "Main Activity Diagram")

###### _Main Sequence Diagram_
![Alt text](https://github.com/emxsys/callattendant/blob/master/docs/images/Main_Sequence_Diagram.png "Main Sequence Diagram")

### Implementation View
 TODO...
 
### Deployment View
###### _Main Deployment Diagram_
![Alt text](https://github.com/emxsys/callattendant/blob/master/docs/images/Main_Deployment_Diagram.png "Main Deployment Diagram")

---

## Software Development Plan
The development plan's [phase objectives](https://github.com/emxsys/callattendant/projects?query=is%3Aopen+sort%3Acreated-asc) are captured in the GitHub projects.
### [Inception Phase](https://github.com/emxsys/callattendant/projects/1)
- Iteration #I1: [v0.1](https://github.com/emxsys/callattendant/releases/tag/v0.1)
### [Elaboration Phase](https://github.com/emxsys/callattendant/projects/2)
- Iteration #E1: v0.2
### [Construction Phase](https://github.com/emxsys/callattendant/projects/3)
- Iteration #C1: v0.3
- Iteration #C2: v0.4
### [Transition Phase](https://github.com/emxsys/callattendant/projects/4)
- Iteration #T1: v1.0

---

## Tools

#### DB Browser for SQLite
```
sudo apt-get install sqlitebrowser
```
```
sqlitebrowser callattendant/src/callattendant.db
```

## Web Pages
##### Call Log
http://localhost:5000/

##### Block List
http://localhost:5000/blacklist

##### Permitted List
http://localhost:5000/whitelist


---

## Related Projects

- [pamapa/callblocker](https://github.com/pamapa/callblocker)
- [pradeesi/Incoming_Call_Detail_Logger ](https://github.com/pradeesi/Incoming_Call_Detail_Logger)
- [pradeesi/record_audio_from_phone_line](https://github.com/pradeesi/record_audio_from_phone_line)
- [pradeesi/play_audio_over_phone_line](https://github.com/pradeesi/play_audio_over_phone_line)



## Installation

### Prequisites

You will need a raspberry pi running raspbian and access to the Internet for
software installation. For the project, you will need a modem of some sort to
do modem stuff.

This modem: https://www.amazon.com/gp/product/B0013FDLM0/ref=ppx_yo_dt_b_asin_image_o03_s00?ie=UTF8&psc=1

has been proven effective. For some installs, it just works, no config needed.
It showed up as /dev/ttyACM0.

### Setup

The installation calls for Python2.X. Yes, it's deprecated, but go ahead and
live dangerously. Set up a virtual environment:

```bash
sudo apt install virtualenv

virtualenv ca_testing --python=python2.7

source ca_testing/bin/activate
```

Now you're operating with a virtual Python. To check, issue the following
command:

```bash

$ which python
```

You should see output of the form:

```
(ca_testing) pi@raspberryi:~/testing $ which python
/home/pi/testing/ca_testing/bin/python
```

To make sure you're on 2.7 as requested, issue:

```bash

$ python --version
```

You should see output of the form:

```
(ca_testing) pi@raspberrypi:~/testing $ python --version
Python 2.7.16
```

#### Install Packages

We've provided a requirements file called `requirements.txt`. Let's use it to
install the required packages.

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
(ca_testing) pi@raspberrypi:~/testing/callattendant/src $ python callattendant.py 
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
