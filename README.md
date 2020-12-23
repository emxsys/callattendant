# Call Attendant
![PyPI](https://img.shields.io/pypi/v/callattendant?style=flat&link=https://pypi.org/project/callattendant/) ![PyPI - License](https://img.shields.io/pypi/l/callattendant?link=https://github.com/emxsys/callattendant/blob/master/LICENSE) ![PyPI - Status](https://img.shields.io/pypi/status/callattendant) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/emxsys/callattendant/callattendant)

#### `pip install callattendant`

The Call Attendant (__callattendant__) is an auto attendant with an integrated call blocker and 
voice messaging system running on a Raspberry Pi. It stops annoying robocalls and spammers from
interrupting your life. Let the Call Attendant intercept and block robocallers and telemarketers
before the first ring on your landline.

The __callattendant__ provides international support with configurable phone number formats, with 
flexible and editable blocked-number and permitted-number lists.

_If you're at all interested in this project, please provide some feedback by giving it a
__[star](https://github.com/emxsys/callattendant/stargazers)__, or even better, get involved
by filing [issues](https://github.com/emxsys/callattendant/issues), joining the 
[forum](https://groups.io/g/callattendant) and/or submitting 
[pull requests](https://github.com/emxsys/callattendant/pulls).
Thanks!_

#### Support Links
- [Web Page](https://emxsys.github.io/callattendant/)
- [Wiki](https://github.com/emxsys/callattendant/wiki)
- [Forum](https://groups.io/g/callattendant)

#### Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)

## Overview
The Call Attendant (__callattendant__) is a python-based, automated call attendant that runs on a
lightweight Raspberry Pi, or other Linux-based system, coupled with a US Robotics 5637 USB modem.

#### How it works
The Raspberry Pi and modem are connected to your home phone system in parallel with your phone
handset(s). When an incoming call is received, the call goes to both your phone and the
__callattendant__. During the period of the first ring the __callattendant__ analyzes the caller ID,
and based on your configuration, determines if the call should be blocked or allowed. Blocked calls
can be simply hung up on, or routed to the voice message system. Calls that are allowed will simply
ring your home phone like normal. Calls can be sent to the integrated voice mail system if you choose. 
The __callattendant__'s filtering mechanisms include an online lookup service, a permitted number list,
a blocked number list and pattern matching on the caller's number and/or name.

#### Features include:
- A call blocker that intercepts robocallers and blocked numbers at or before the first ring
- Permitted numbers pass straight through to the local phone system for normal call ringing and answering
- Visual indicators to show whether the incoming call is from a permitted, blocked, or unknown number
- Call details, permitted numbers, and blocked numbers are available in a web-based user interface
- Calls can be handled by a voice messaging system that optioanlly requires human interaction,
e.g, "Press 1 to leave a message"

You can review call history, voice messages, permitted and blocked numbers, and performing caller
management through the Call Attendant's web interface. Here is an example of the home page with metrics
and a convienient list of recent calls. For a complete description see the
[User Guide](https://github.com/emxsys/callattendant/wiki/User-Guide).

##### _Screenshots of the home page as seen on an IPad Pro and a Pixel 2 phone_
![Dashboard-Responsive](https://github.com/emxsys/callattendant/raw/master/docs/dashboard-responsive.png)

### Documentation
The project wiki on GitHub contains the documentation for the Call Attendant:

- See the [Wiki Home](https://github.com/emxsys/callattendant/wiki/Home) for complete
installation, configuration, and operation instructions.
- See the [User Guide](https://github.com/emxsys/callattendant/wiki/User-Guide) section for the
web interface instructions.
- The [Developer Guide](https://github.com/emxsys/callattendant/wiki/Developer-Guide) section
describes the software architecture and software development plan, and shows you how to setup
your software development environment.
- The [Advanced](https://github.com/emxsys/callattendant/wiki/Advanced) section addresses more
complex setups and situations. For instance, _Running as a Service_.


### Hardware Requirements
The __callattendant__ uses the following hardware:
- [Raspberry Pi 3B+](https://www.amazon.com/ELEMENT-Element14-Raspberry-Pi-Motherboard/dp/B07P4LSDYV/ref=sr_1_4?dchild=1&keywords=raspberry+pi+3&qid=1598057138&sr=8-4) or better
- [US Robotics 5637 Modem](https://www.amazon.com/gp/product/B0013FDLM0/ref=ppx_yo_dt_b_asin_image_o03_s00?ie=UTF8&psc=1) 
or the [Zoom 3095 Modem](https://www.amazon.com/Zoom-Model-3095-USB-Modem/dp/B07HHKG6HR). Other Conexant-based
modems may work.

##### _Photo of the required hardware: a Raspberry Pi 3B+ and USR5637 modem_
![Raspberry Pi and USR5637 Modem](https://github.com/emxsys/callattendant/raw/master/docs/raspberry_pi-modem.jpg)

---

## Quick Start

### Hardware
You will need a Raspberry Pi running Raspbian or better with access to the Internet for the software
installation, and ultimately for the the online robocaller lookups. For the project, you will need a
modem of some sort to do the telephony communications. The **U.S. Robotics USR5637 56K USB Modem** has
been proven effective. For some installs, it just works, no config needed. It showed up as /dev/ttyACM0.

---

### Software
The installation calls for Python3.X.

#### Setup a Virtual Environment
###### _Optional_
The following instructions create and activate a virtual environment named _venv_ within the
current folder:
```bash
# Install virtualenv - if not installed
sudo apt install virtualenv

# Create the virtual environment
virtualenv venv --python=python3

# Activate it
source venv/bin/activate
```

Now you're operating with a virtual Python. To check, issue the `which` command and ensure the
output points to your virtual environment; and also check the Python version:
```bash
$ which python
/home/pi/venv/bin/python

$ python --version
Python 3.7.3
```
Later, when you install the __callattendant__ software, it will be placed within the virtual environment
folder (under `lib/python3.x/site-packages` to be exact). The virtual environment, when activated, alters
your _PATH_ so that the system looks for python and its packages within this folder hierarchy.

#### Install the Software
The software is available on [PyPI](https://pypi.org/project/callattendant/). Install and update using `pip`:
```bash
# Using the virtual environment you use "pip" to install the software
pip install callattendant

# You must use "pip3" on the Pi if your not using a virtual environment
pip3 install callattendant
```

If your not using the virtual environment, you may need to reboot or logoff/login to update the
`$PATH` for your profile in order to find and use the `callattendant` command.

---

### Operation

The __callattendant__ package includes a `callattendant` command to start the system. Run this command
the first time with the `--create-folder` option to create the initial data and files in the default
data folder: `~/.callattendant`. This is a hidden folder off the root of your home directory. You
can override this location with the `--data-path` option.

```
Usage: callattendant --config [FILE] --data-path [FOLDER]
Options:
-c, --config [FILE]       load a python configuration file
-d, --data-path [FOLDER]  path to data and configuration files
-f, --create-folder       create the data-path folder if it does not exist
-h, --help                displays this help text
```

```bash
# Creating the default data folder with the default configuration
callattendant --create-folder

# Using the default configuration
callattendant

# Using a customized config file in an alternate, existing location
callattendant --config myapp.cfg --data-path /var/lib/callattendant
```

You should see output of the form:
```
Command line options:
  --config=app.cfg
  --data-path=None
  --create-folder=False
[Configuration]
  BLOCKED_ACTIONS = ('greeting', 'voice_mail')
  BLOCKED_GREETING_FILE = /home/pi/.local/lib/python3.7/site-packages/callattendant/resources/blocked_greeting.wav
  BLOCKED_RINGS_BEFORE_ANSWER = 0
  BLOCK_ENABLED = True
  BLOCK_NAME_PATTERNS = {'V[0-9]{15}': 'Telemarketer Caller ID'}
  BLOCK_NUMBER_PATTERNS = {}
  BLOCK_SERVICE = NOMOROBO
  CONFIG_FILE = app.cfg
  DATABASE = callattendant.db
  DATA_PATH = /home/pi/.callattendant
  DB_FILE = /home/pi/.callattendant/callattendant.db
  DEBUG = False
  ENV = production
  PERMITTED_ACTIONS = ('greeting', 'record_message')
  PERMITTED_GREETING_FILE = /home/pi/.local/lib/python3.7/site-packages/callattendant/resources/general_greeting.wav
  PERMITTED_RINGS_BEFORE_ANSWER = 6
  PERMIT_NAME_PATTERNS = {}
  PERMIT_NUMBER_PATTERNS = {}
  PHONE_DISPLAY_FORMAT = ###-###-####
  PHONE_DISPLAY_SEPARATOR = -
  ROOT_PATH = /home/pi/.local/lib/python3.7/site-packages/callattendant
  SCREENED_ACTIONS = ('greeting', 'record_message')
  SCREENED_GREETING_FILE = /home/pi/.local/lib/python3.7/site-packages/callattendant/resources/general_greeting.wav
  SCREENED_RINGS_BEFORE_ANSWER = 0
  SCREENING_MODE = ('whitelist', 'blacklist')
  TESTING = False
  VERSION = 1.1.0
  VOICE_MAIL_GOODBYE_FILE = /home/pi/.local/lib/python3.7/site-packages/callattendant/resources/goodbye.wav
  VOICE_MAIL_GREETING_FILE = /home/pi/.local/lib/python3.7/site-packages/callattendant/resources/general_greeting.wav
  VOICE_MAIL_INVALID_RESPONSE_FILE = /home/pi/.local/lib/python3.7/site-packages/callattendant/resources/invalid_response.wav
  VOICE_MAIL_LEAVE_MESSAGE_FILE = /home/pi/.local/lib/python3.7/site-packages/callattendant/resources/please_leave_message.wav
  VOICE_MAIL_MENU_FILE = /home/pi/.local/lib/python3.7/site-packages/callattendant/resources/voice_mail_menu.wav
  VOICE_MAIL_MESSAGE_FOLDER = /home/pi/.callattendant/messages
Initializing Modem
Opening serial port
Looking for modem on /dev/ttyACM0
******* Conextant-based modem detected **********
Serial port opened on /dev/ttyACM0
Modem initialized
{MSG LED OFF}
Starting the Flask webapp
Running the Flask server
Waiting for call...
 * Serving Flask app "userinterface.webapp" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off

```

Make a few calls to yourself to test the service. The standard output will show the
progress of the calls. Then navigate to `http://<pi-address>|<pi-hostname>:5000` in a
web browser to checkout the web interface.

Press `ctrl-c` to shutdown the system

---

### Web Interface
#### URL: `http://<pi-address>|<pi-hostname>:5000`
To view the web interface, simply point your web browser to port `5000` on your Raspberry Pi.
For example, in your Raspberry Pi's browser, you can use:
```
http://localhost:5000/
```

See the [User Guide](https://github.com/emxsys/callattendant/wiki/User-Guide) for more information.

---

### Configuration
The Call Attendant's behavior can be controlled by a configuration file. To override the default
configuration, open the  the `~/.callattenant/app.cfg` and edit its contents.

```bash
nano ~/.callattendant/app.cfg
```

Then specify the configuration file and path on the command line, e.g.:
```
callattendant --config app.cfg
```
See the [Configuration](https://github.com/emxsys/callattendant/wiki/Home#configuration)
section in the project's wiki for more information.

---
