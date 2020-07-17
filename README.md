# Call Attendant
Automated call attendant, call blocker, and voice messaging on a Raspberry Pi.

#### Table of Contents
- [Overview](#overview)
- [Software Architecture](#software-architecture)
- [Software Development Plan](#software-development-plan)

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




