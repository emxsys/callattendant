#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# file: modem.py
#
# Copyright 2018 Bruce Schubert <bruce@emxsys.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# ==============================================================================
# This code was inspired by and contains code snippets from Pradeep Singh:
# https://iotbytes.wordpress.com/incoming-call-details-logger-with-raspberry-pi/
# https://github.com/pradeesi/Incoming_Call_Detail_Logger
# ==============================================================================

import atexit
import os
import re
import serial
import subprocess
import sys
import threading
import time
import wave

from datetime import datetime
from pprint import pprint

from hardware.indicators import RingIndicator

# ACSII codes
DLE_CODE = chr(16)      # Data Link Escape (DLE) code
ETX_CODE = chr(3)       # End Transmission (ETX) code
CR_CODE = chr(13)       # Carraige return
LF_CODE = chr(10)       # Line feed

# Supported modem product codes returned by ATI0
USR_5637_PRODUCT_CODE = b'5601'
ZOOM_3905_PRODUCT_CODE = b'56000'

#  Modem AT commands:
#  See http://support.usr.com/support/5637/5637-ug/ref_data.html
RESET = "ATZ"
GET_MODEM_PRODUCT_CODE = "ATI0"
GET_MODEM_SETTINGS = "ATI4"         # USR only. Zoom modem returns empty string
DISABLE_ECHO_COMMANDS = "ATE0"
ENABLE_ECHO_COMMANDS = "ATE1"
ENABLE_FORMATTED_CID = "AT+VCID=1"
ENABLE_VERBOSE_CODES = "ATV1"
DISABLE_SILENCE_DETECTION = "AT+VSD=128,0"
ENABLE_SILENCE_DETECTION_5_SECS = "AT+VSD=128,50"
ENABLE_SILENCE_DETECTION_10_SECS = "AT+VSD=128,100"
ENTER_VOICE_MODE = "AT+FCLASS=8"
ENTER_VOICE_RECIEVE_DATA_STATE = "AT+VRX"
ENTER_VOICE_TRANSMIT_DATA_STATE = "AT+VTX"
ENTER_TAD_OFF_HOOK = "AT+VLS=1"  # Telephone Answering Device (TAD) off-hook, connected to telco
SEND_VOICE_TONE_BEEP = "AT+VTS=[933,900,120]"   # 1.2 second beep
GET_VOICE_COMPRESSION_SETTING = "AT+VSM?"
GET_VOICE_COMPRESSION_OPTIONS = "AT+VSM=?"
SET_VOICE_COMPRESSION = ""  # Set by modem detection function
SET_VOICE_COMPRESSION_USR = "AT+VSM=128,8000"     # USR 5637: 128 = 8-bit linear, 8.0 kHz
SET_VOICE_COMPRESSION_ZOOM = "AT+VSM=1,8000,0,0"  # Zoom 3095:  1 = 8-bit unsigned pcm, 8.0 kHz
GO_OFF_HOOK = "ATH1"
GO_ON_HOOK = "ATH0"
TERMINATE_CALL = "ATH"

# Modem DLE shielded codes - DCE to DTE modem data
DCE_ANSWER_TONE = (chr(16) + chr(97)).encode()          # <DLE>-a
DCE_BUSY_TONE = (chr(16) + chr(98)).encode()            # <DLE>-b
DCE_FAX_CALLING_TONE = (chr(16) + chr(99)).encode()     # <DLE>-c
DCE_DIAL_TONE = (chr(16) + chr(100)).encode()           # <DLE>-d
DCE_DATA_CALLING_TONE = (chr(16) + chr(101)).encode()   # <DLE>-e
DCE_PHONE_ON_HOOK = (chr(16) + chr(104)).encode()       # <DLE>-h
DCE_PHONE_OFF_HOOK = (chr(16) + chr(72)).encode()       # <DLE>-H
DCE_RING = (chr(16) + chr(82)).encode()                 # <DLE>-R
DCE_SILENCE_DETECTED = (chr(16) + chr(115)).encode()    # <DLE>-s
DCE_TX_BUFFER_UNDERRUN = (chr(16) + chr(117)).encode()  # <DLE>-u
DCE_END_VOICE_DATA_TX = (chr(16) + chr(3)).encode()     # <DLE><ETX>

# System DLE shielded codes (single DLE) - DTE to DCE commands
DTE_RAISE_VOLUME = (chr(16) + chr(117))           # <DLE>-u
DTE_LOWER_VOLUME = (chr(16) + chr(100))           # <DLE>-d
DTE_END_VOICE_DATA_TX = (chr(16) + chr(3))        # <DLE><ETX>
DTE_CLEAR_TRASMIT_BUFFER = (chr(16) + chr(24))    # <DLE><CAN>
DTE_END_RECIEVE_DATA_STATE = (chr(16) + chr(33))  # <DLE>-!

# Return codes
CRLF = (chr(13) + chr(10)).encode()

# Record Voice Mail variables
REC_VM_MAX_DURATION = 120  # Time in Seconds

TEST_DATA = [
    b"RING", b"DATE=0801", b"TIME=1801", b"NMBR=8055554567", b"NAME=Test1 - Permitted", b"RING", b"RING", b"RING", b"RING",
    b"RING", b"DATE=0801", b"TIME=1800", b"NMBR=5551234567", b"NAME=Test2 - Spammer",
    b"RING", b"DATE=0801", b"TIME=1802", b"NMBR=3605554567", b"NAME=Test3 - Blocked",
    b"RING", b"DATE=0801", b"TIME=1802", b"NMBR=8005554567", b"NAME=V123456789012345",
]


class Modem(object):
    """
    This class is responsible for serial communications between the
    Raspberry Pi and a voice/data/fax modem.
    """

    def __init__(self, config, handle_caller):
        """
        Constructs a modem object for serial communications.
            :param config:
                application configuration dict
            :param handle_caller:
                callback function that takes a caller dict
        """
        self.config = config
        self.handle_caller = handle_caller
        self.model = None

        # Thread synchronization object
        self._lock = threading.RLock()

        # Ring notifications
        self.ring_indicator = RingIndicator(
            self.config.get("GPIO_LED_RING_PIN"),
            self.config.get("GPIO_LED_RING_BRIGHTNESS", 100))
        self.ring_event = threading.Event()

        # Setup and open the serial port
        self._serial = serial.Serial()

    def handle_calls(self):
        """
        Starts the thread that processes incoming data.
        """
        # TODO Pass in call handler here instead of ctor
        self._init_modem()
        self.event_thread = threading.Thread(target=self._call_handler)
        self.event_thread.name = "modem_call_handler"
        self.event_thread.start()

    def _call_handler(self):
        """
        Thread function that processes the incoming modem data.
        """
        # Common constants
        RING = "RING".encode("utf-8")
        DATE = "DATE".encode("utf-8")
        TIME = "TIME".encode("utf-8")
        NAME = "NAME".encode("utf-8")
        NMBR = "NMBR".encode("utf-8")

        # Testing variables
        dev_mode = self.config["ENV"] == "development"
        debugging = self.config["DEBUG"]
        testing = self.config["TESTING"]
        test_index = 0
        logfile = None

        # Save the modem data to a file for development purposes
        if dev_mode:
            print("Saving raw modem data to modem.log")
            filename = os.path.join(self.config["DATA_PATH"], "modem.log")
            logfile = open(filename, 'ab')

        # Handle incoming calls
        try:
            # This loop reads incoming data from the serial port and
            # posts the caller data to the handle_caller function
            call_record = {}
            while 1:
                modem_data = b''

                # Read from the modem
                with self._lock:
                    if testing:
                        # Iterate thru the test data
                        if test_index >= len(TEST_DATA):
                            break
                        modem_data = TEST_DATA[test_index]
                        test_index += 1
                    else:
                        # Wait/read a line of data from the serial port.
                        # The verbose-form code is preceded and terminated by the
                        # sequence <CR><LF>. The numeric-form is also terminated
                        # by <CR>, but it has no preceding sequence.
                        modem_data = self._serial.readline()

                # Process the modem data
                if modem_data != b'' and modem_data != CRLF:
                    if debugging:
                        print(modem_data)
                    if dev_mode:
                        logfile.write(modem_data)
                        logfile.flush()

                    if RING in modem_data:
                        # Notify other threads that a ring occurred
                        self.ring_event.set()
                        self.ring_event.clear()
                        # Visual notification (LED)
                        self.ring_indicator.ring()
                    # Extract caller info
                    if DATE in modem_data:
                        call_record['DATE'] = decode(modem_data[5:])
                    if TIME in modem_data:
                        call_record['TIME'] = decode(modem_data[5:])
                    if NAME in modem_data:
                        call_record['NAME'] = decode(modem_data[5:])
                    if NMBR in modem_data:
                        call_record['NMBR'] = decode(modem_data[5:])

                    # https://stackoverflow.com/questions/1285911/how-do-i-check-that-multiple-keys-are-in-a-dict-in-a-single-pass
                    if all(k in call_record for k in ("DATE", "TIME", "NAME", "NMBR")):
                        # Queue caller for screening
                        print("> Queueing call {} for processing".format(call_record["NMBR"]))
                        self.handle_caller(call_record)
                        call_record = {}

        finally:
            if dev_mode:
                print("Closing modem log file")
                logfile.close()

    def pick_up(self):
        """
        Go "off hook". Called by the application object (callattendant.py)
        to set the lock and perform a batch of operations before hanging up.
        The hang_up() function must be called to release the lock.

        note:: hang_up() MUST be called by the same thread to release the lock
        """
        print("> Going off hook...")
        self._serial.cancel_read()
        self._lock.acquire()
        if self.config["DEBUG"]:
            print(">>> Lock acquired in pick-up()")
        try:
            if not self._send(ENTER_VOICE_MODE):
                raise RuntimeError("Failed to put modem into voice mode.")

            if not self._send(DISABLE_SILENCE_DETECTION):
                raise RuntimeError("Failed to disable silence detection.")

            if not self._send(ENTER_TAD_OFF_HOOK):
                raise RuntimeError("Unable put modem into telephone answering device mode.")

            # Flush any existing input outout data from the buffers
            # self._serial.flushInput()
            # self._serial.flushOutput()

        except Exception as e:
            pprint(e)
            # Only release the lock if we failed to go off-hook
            self._lock.release()
            print(">>> Lock released in pick-up()")
            return False

        return True

    def hang_up(self):
        """
        Hang up on an active call, i.e., go "on hook". Called by the
        application object after finishing a batch of modem operations
        to terminate the call and release the lock aquired by pick_up().
        note:: Assumes pick-up() has been called previously to acquire
            the lock
        """
        print("> Going on hook...")
        try:
            self._serial.cancel_read()

            # Prevent any pending data from corrupting the next call
            self._serial.flushInput()
            self._serial.flushOutput()

            if not self._send(GO_ON_HOOK):
                raise RuntimeError("Failed to hang up the call.")
            # ~ if not self._send(RESET):
                # ~ raise RuntimeError("Failed to reset the modem.")

        except Exception as e:
            print("**Error: hang_up() failed")
            pprint(e)
            return False

        finally:
            # Release the lock acquired by pick_up()
            self._lock.release()
            if self.config["DEBUG"]:
                print(">>> Lock released in hang-up()")

        return True

    def play_audio(self, audio_file_name):
        """
        Play the given audio file.
            :param audio_file_name:
                a wav file with 8-bit linear compression recored at 8.0 kHz sampling rate
        """
        if self.config["DEBUG"]:
            print("> Playing {}...".format(audio_file_name))

        self._serial.cancel_read()
        with self._lock:

            # Setup modem for transmitting audio data
            if not self._send(ENTER_VOICE_MODE):
                print("* Error: Failed to put modem into voice mode.")
                return False
            if not self._send(SET_VOICE_COMPRESSION):
                print("* Error: Failed to set compression method and sampling rate specifications.")
                return False
            if not self._send(ENTER_TAD_OFF_HOOK):
                print("* Error: Unable put modem into telephone answering device mode.")
                return False
            if not self._send(ENTER_VOICE_TRANSMIT_DATA_STATE, "CONNECT"):
                print("* Error: Unable put modem into voice data transmit state.")
                return False

            # Play Audio File
            with wave.open(audio_file_name, 'rb') as wavefile:
                sleep_interval = .12  # 120ms; You may need to change to smooth-out audio
                chunk = 1024
                data = wavefile.readframes(chunk)
                while data != b'':
                    self._serial.write(data)
                    data = wavefile.readframes(chunk)
                    # ~ time.sleep(sleep_interval)

                self._send(DTE_END_VOICE_DATA_TX)

        return True

    def record_audio(self, audio_file_name):
        """
        Records audio from the model to the given audio file.
            :param audio_file_name:
                the wav file to be created with the recorded audio;
                recorded with 8-bit linear compression at 8.0 kHz sampling rate
        """
        if self.config["DEBUG"]:
            print("> Recording {}...".format(audio_file_name))

        debugging = self.config["DEBUG"]

        self._serial.cancel_read()
        with self._lock:
            try:
                if not self._send(ENTER_VOICE_MODE):
                    raise RuntimeError("Failed to put modem into voice mode.")

                if not self._send("AT+VGT=128"):
                    raise RuntimeError("Failed to set speaker volume to normal.")

                if not self._send(SET_VOICE_COMPRESSION):
                    raise RuntimeError("Failed to set compression method and sampling rate specifications.")

                if not self._send(DISABLE_SILENCE_DETECTION):
                    raise RuntimeError("Failed to disable silence detection.")

                if not self._send(ENTER_TAD_OFF_HOOK):
                    raise RuntimeError("Unable put modem into telephone answering device mode.")

                # Play 1.2 beep
                if not self._send(SEND_VOICE_TONE_BEEP):
                    raise RuntimeError("Failed to play 1.2 second beep.")

                if not self._send(ENABLE_SILENCE_DETECTION_5_SECS):
                    raise RuntimeError("Failed to enable silence detection.")

                if not self._send(ENTER_VOICE_RECIEVE_DATA_STATE, "CONNECT"):
                    raise RuntimeError("Error: Unable put modem into voice receive mode.")

            except RuntimeError as error:
                print("Modem initialization error: ", error)
                return False

            # Record Audio File
            start_time = datetime.now()
            CHUNK = 1024
            audio_frames = []
            while 1:
                # Read audio data from the Modem

                audio_data = self._serial.read(CHUNK)

                if (DCE_PHONE_OFF_HOOK in audio_data):
                    print(">> Local phone off hook... Stop recording")
                    break

                if (DCE_RING in audio_data):
                    print(">> Ring detected... Stop recording; new call coming in")
                    break

                # Check if <DLE>b is in the stream
                if (DCE_BUSY_TONE in audio_data):
                    print(">> Busy Tone... Stop recording.")
                    break

                # Check if <DLE>s is in the stream
                if (DCE_SILENCE_DETECTED in audio_data):
                    print(">> Silence Detected... Stop recording.")
                    break

                # Check if <DLE><ETX> is in the stream
                if (DCE_END_VOICE_DATA_TX in audio_data):
                    print(">> <DLE><ETX> Char Recieved... Stop recording.")
                    break

                # Timeout
                if ((datetime.now() - start_time).seconds) > REC_VM_MAX_DURATION:
                    print(">> Stop recording: max time limit reached.")
                    break

                # Add Audio Data to Audio Buffer
                audio_frames.append(audio_data)

            # Save the Audio into a .wav file
            with wave.open(audio_file_name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(1)
                wf.setframerate(8000)
                wf.writeframes(b''.join(audio_frames))
            print(">> Recording stopped after {} seconds".format((datetime.now() - start_time).seconds))

            # Clear input buffer before sending commands else its
            # contents may interpreted as the cmd's return code
            self._serial.reset_input_buffer()

            # Send End of Recieve Data state by passing "<DLE>!"
            response = ""
            if self.model == "ZOOM":
                response = "OK"
            elif self.model == "USR":
                # Note: the command returns <DLE><ETX>, but the  DLE is stripped
                # from the response during the test, so we only test for the ETX.
                response = ETX_CODE
            if not self._send(DTE_END_RECIEVE_DATA_STATE, response):
                print("* Error: Unable to signal end of data receive state")

        return True

    def wait_for_keypress(self, wait_time_secs=15):
        """
        Waits n seconds for a key-press.
            :params wait_time_secs:
                the number of seconds to wait for a keypress
            :return:
                success (bool), key-press value (str)
        """
        print("> Waiting for key-press...")

        debugging = self.config["DEBUG"]

        self._serial.cancel_read()
        with self._lock:
            try:
                # Initialize modem
                if not self._send(ENTER_VOICE_MODE):
                    raise RuntimeError("Failed to put modem into voice mode.")

                if not self._send(ENABLE_SILENCE_DETECTION_10_SECS):
                    raise RuntimeError("Failed to enable silence detection.")

                if not self._send(ENTER_TAD_OFF_HOOK):
                    raise RuntimeError("Unable put modem into Telephone Answering Device mode.")

                # Wait for keypress
                start_time = datetime.now()
                modem_data = b''
                while 1:
                    # Read 1 bytes from the Modem into the buffer
                    modem_data = modem_data + self._serial.read(1)
                    if debugging:
                        pprint(modem_data)

                    if (DCE_PHONE_OFF_HOOK in modem_data):
                        raise RuntimeError("Local phone off hook... Aborting.")

                    if (DCE_RING in modem_data):
                        raise RuntimeError("Ring detected... Aborting.")

                    if (DCE_BUSY_TONE in modem_data):
                        raise RuntimeError("Busy Tone... Aborting.")

                    if (DCE_SILENCE_DETECTED in modem_data):
                        raise RuntimeError("Silence Detected... Aborting.")

                    if (DCE_END_VOICE_DATA_TX in modem_data):
                        raise RuntimeError("<DLE><ETX> Recieved... Aborting.")

                    if ((datetime.now() - start_time).seconds) > wait_time_secs:
                        raise RuntimeError("Timeout - wait time limit reached.")

                    # Parse DTMF Digits, if found in the modem data
                    digit_list = re.findall('[0-9]+', decode(modem_data))  # '/(.+?)~'
                    if len(digit_list) > 0:
                        if debugging:
                            print("DTMF Digits:")
                            pprint(digit_list)
                        return True, digit_list[0]

            except RuntimeError as e:
                print("Wait for key-press: {}".format(e))

        return False, ''

    def _send(self, command, expected_response="OK", response_timeout=5):
        """
        Sends a command string (e.g., AT command) to the modem.
            :param command:
                the command string to send
            :param expected_response:
                the expected response to the command, e.g. "OK"
            :param response_timeout:
                number of seconds to wait for the command to respond
            :return:
                True: if the command response matches the expected_response;
        """
        success, result = self._send_and_read(command, expected_response, response_timeout)
        return success

    def _send_and_read(self, command, expected_response="OK", response_timeout=5):
        """
        Sends a command string (e.g., AT command) to the modem and reads the result
            :param command:
                the command string to send
            :param expected_response:
                the expected response to the command, e.g. "OK"
            :param response_timeout:
                number of seconds to wait for the command to respond
            :return:
                True: if the command response matches the expected_response;
                plus the result preceeding the command response, if any.
        """
        with self._lock:
            try:
                if self.config["DEBUG"]:
                    print(command)

                self._serial.write((command + '\r').encode())
                self._serial.flush()
                # Get the execution status plus any preceeding result(s) from the modem
                success, result =  self._read_response(expected_response, response_timeout)
                return (success, result)
            except Exception as e:
                print(e)
                print("Error: Failed to execute the command: {}".format(command))
                return False, None

    def _read_response(self, expected_response, response_timeout_secs):
        """
        Handles the command response code from the modem.
        Called by _send() and operates within the _send method's lock context.
            :param expected response:
                the expected response, e.g. "OK"
            :param response_timeout_secs:
                number of seconds to wait for the command to respond
            :return: (boolean, result)
                True if the response matches the expected_response or False
                if ERROR is returned or if it times out; followed by any preceeding
                value(s) returned by the modem.
        """
        start_time = datetime.now()
        try:
            result = b''
            self._serial.flushInput()
            while 1:
                modem_data = self._serial.readline()
                result += modem_data
                if self.config["DEBUG"]:
                    pprint(modem_data)
                response = decode(modem_data)  # strips DLE_CODE

                if expected_response == None:
                    return (True, None)

                elif expected_response == response:
                    return (True, result)

                elif "ERROR" in response:
                    if self.config["DEBUG"]:
                        print(">>> _read_response returned ERROR")
                    return (False, result)

                elif (datetime.now() - start_time).seconds > response_timeout_secs:
                    if self.config["DEBUG"]:
                        print(">>> _read_response timed out")
                    return (False, result)

        except Exception as e:
            print("Error in read_response function...")
            print(e)
            return (False, None)

    def _init_modem(self):
        """Auto-detects and initializes the modem."""
        # Detect and open the Modem Serial COM Port
        try:
            self.open_serial_port()
        except Exception as e:
            print(e)
            print("Error: Unable to open the Serial Port.")
            sys.exit()

        # Initialize the Modem
        try:
            # Flush any existing input outout data from the buffers
            self._serial.flushInput()
            self._serial.flushOutput()

            # Test Modem connection, using basic AT command.
            if not self._send("AT"):
                print("Error: Unable to access the Modem")
            if not self._send(FACTORY_RESET):
                print("Error: Unable reset to factory default")
            if not self._send(ENABLE_VERBOSE_CODES):
                print("Error: Unable set response in verbose form")
            if not self._send(DISABLE_ECHO_COMMANDS):
                print("Error: Failed to disable local echo mode")
            if not self._send(ENABLE_FORMATTED_CID):
                print("Error: Failed to enable formatted caller report.")

            # Save these settings to a profile
            if not self._send("AT&W0"):
                print("Error: Failed to store profile.")

            self._send(DISPLAY_MODEM_SETTINGS)

            # Flush any existing input outout data from the buffers
            self._serial.flushInput()
            self._serial.flushOutput()

            # Automatically close the serial port at program termination
            atexit.register(self.close_serial_port)

        except Exception as e:
            print(e)
            print("Error: unable to Initialize the Modem")
            sys.exit()

    def _init_serial_port(self, com_port):
        """Initializes the given COM port for communications with the modem."""
        self._serial.port = com_port
        self._serial.baudrate = 57600                   # 9600
        self._serial.bytesize = serial.EIGHTBITS        # number of bits per bytes
        self._serial.parity = serial.PARITY_NONE        # set parity check: no parity
        self._serial.stopbits = serial.STOPBITS_ONE     # number of stop bits
        self._serial.timeout = 3                        # non-block read
        self._serial.writeTimeout = 3                   # timeout for write
        self._serial.xonxoff = False                    # disable software flow control
        self._serial.rtscts = False                     # disable hardware (RTS/CTS) flow control
        self._serial.dsrdtr = False                     # disable hardware (DSR/DTR) flow control

    def _detect_modem(self):

        global SET_VOICE_COMPRESSION, ENABLE_SILENCE_DETECTION_5_SECS, \
                DTE_RAISE_VOLUME, DTE_LOWER_VOLUME, DTE_END_VOICE_DATA_TX, \
                DTE_END_RECIEVE_DATA_STATE, DTE_CLEAR_TRASMIT_BUFFER

        # Attempt to identify the modem
        success, result = self._send_and_read(GET_MODEM_PRODUCT_CODE)
        if success:
            if ZOOM_3905_PRODUCT_CODE in result:
                print("******* Zoom Model 3905 Detected **********")
                self.model = "ZOOM"
                # Define the compression settings
                SET_VOICE_COMPRESSION = SET_VOICE_COMPRESSION_ZOOM
                # ~ ENABLE_SILENCE_DETECTION_5_SECS = "AT+VSD=0,50"
                # System DLE shielded codes (double DLE) - DTE to DCE commands
                DTE_RAISE_VOLUME = (chr(16) + chr(16) + chr(117))               # <DLE><DLE>-u
                DTE_LOWER_VOLUME = (chr(16) + chr(16) + chr(100))               # <DLE><DLE>-d
                DTE_END_VOICE_DATA_TX = (chr(16) + chr(16) + chr(16) + chr(3))  # <DLE><DLE><DLE><ETX>
                DTE_END_RECIEVE_DATA_STATE = (chr(16) + chr(16) + chr(16) + chr(33))  # <DLE><DLE><DLE>-!
                DTE_CLEAR_TRASMIT_BUFFER = (chr(16) + chr(16) + chr(24)) # <DLE><DLE><CAN>
            elif USR_5637_PRODUCT_CODE in result:
                print("******* US Robotics Model 5637 detected **********")
                self.model = "USR"
                # Define the compression settings
                SET_VOICE_COMPRESSION = SET_VOICE_COMPRESSION_USR
                # System DLE shielded codes (single DLE) - DTE to DCE commands
                DTE_RAISE_VOLUME = (chr(16) + chr(117))           # <DLE>-u
                DTE_LOWER_VOLUME = (chr(16) + chr(100))           # <DLE>-d
                DTE_END_VOICE_DATA_TX = (chr(16) + chr(3))        # <DLE><ETX>
                DTE_END_RECIEVE_DATA_STATE = (chr(16) + chr(33))  # <DLE>-!
            else:
                print("******* Unknown modem detected **********")
                # We'll try to use it with the defined AT commands if it supports VOICE mode
                # Validate modem selection by trying to put it in Voice Mode
                if self._send(ENTER_VOICE_MODE):
                    self.model = "UNKNOWN"
                else:
                    print("Error: Failed to put modem into voice mode.")
                    success = False
        return success

    def open_serial_port(self):
        """Detects and opens the serial port attached to the modem."""
        # List all the Serial COM Ports on Raspberry Pi
        proc = subprocess.Popen(['ls /dev/tty[A-Za-z]*'], shell=True, stdout=subprocess.PIPE)
        com_ports = proc.communicate()[0]
        # In order to split, need to pass a bytes-like object
        com_ports_list = com_ports.split(b'\n')

        # Find the right port associated with the Voice Modem
        found = False
        for com_port in com_ports_list:
            if b'tty' in com_port:
                # Try to open the COM Port and execute AT Command
                try:
                    # Initialize the serial port and attempt to open
                    self._init_serial_port(com_port.decode("utf-8"))
                    self._serial.open()
                except Exception as e:
                    print(e)
                    print("Unable to open COM Port: " + str(com_port.decode("utf-8")))
                    pass
                else:
                    # Detect the modem model
                    if not self._detect_modem():
                        print("Error: Failed to detect a compatible modem.")
                        if self._serial.isOpen():
                            self._serial.close()
                    else:
                        # Found a compatible modem on the COM Port - exit the loop
                        print("Modem COM Port is: " + com_port.decode("utf-8"))
                        self._serial.flushInput()
                        self._serial.flushOutput()
                        return True
        return False

    def close_serial_port(self):
        """Closes the serial port attached to the modem."""
        print("Closing Serial Port")
        try:
            if self._serial.isOpen():
                self._serial.close()
                print("Serial Port closed...")
        except Exception as e:
            print(e)
            print("Error: Unable to close the Serial Port.")
            sys.exit()

def decode(bytestr):
    # Remove non-printable chars before decoding.
    string = re.sub(b'[^\x00-\x7f]', b'', bytestr).decode("utf-8").strip(' \t\n\r' + DLE_CODE)
    return string
