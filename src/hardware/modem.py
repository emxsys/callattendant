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

from datetime import datetime
from pprint import pprint
import atexit
import os
import serial
import subprocess
import sys
import threading
import time
import wave


# ACSII codes
DLE_CODE = chr(16)  # Data Link Escape code
ETX_CODE = chr(3)  # End Transmission code

#  Modem AT commands:
#  See http://support.usr.com/support/5637/5637-ug/ref_data.html
DISPLAY_MODEM_SETTINGS = "ATI4"
ENABLE_ECHO_COMMANDS = "ATE1"
ENABLE_FORMATTED_CID = "AT+VCID=1"
ENABLE_VERBOSE_CODES = "ATV1"
ENTER_VOICE_MODE = "AT+FCLASS=8"
ENTER_TELEPHONE_ANSWERING_DEVICE_MODE = "AT+VLS=1"  # DCE off-hook
ENTER_VOICE_TRANSMIT_DATA_STATE = "AT+VTX"
END_VOICE_TRANSMIT_DATA_STATE = DLE_CODE + ETX_CODE
FACTORY_RESET = "ATZ3"
GO_OFF_HOOK = "ATH1"
GO_ON_HOOK = "ATH0"
SET_VOICE_COMPRESSION_METHOD = "AT+VSM=128,8000"  # 128 = 8-bit linear, 8.0 kHz
TERMINATE_CALL = "ATH"

# Record Voice Mail variables
REC_VM_MAX_DURATION = 120  # Time in Seconds

TEST_DATA = [
    "RING", "DATE=0801", "TIME=1800", "NMBR=5551234567", "NAME=Test1 - Spammer",
    "RING", "DATE=0801", "TIME=1801", "NMBR=8055554567", "NAME=Test2 - Permitted",
    "RING", "DATE=0801", "TIME=1802", "NMBR=3605554567", "NAME=Test3 - Blocked",
    "RING", "DATE=0801", "TIME=1802", "NMBR=3605554567", "NAME=V123456789012345",
]

class Modem(object):
    """
    This class is responsible for serial communications between the
    Raspberry Pi and a US Robotics 5637 modem.
    """

    def __init__(self, config, phone_ringing, handle_caller):
        """
        Constructs a modem object for serial communications.
            :param config: application configuration dict
            :param phone_ringing: function that takes a boolean
            :param handle_caller: callback function that takes a caller
        """
        self.config = config
        self.phone_ringing = phone_ringing
        self.handle_caller = handle_caller
        # Thread synchronization object
        self._lock = threading.RLock()
        # Setup and open the serial port
        self._serial = serial.Serial()

    def handle_calls(self):
        self._init_modem()
        self.event_thread = threading.Thread(target=self._call_handler)
        self.event_thread.start()

    def _call_handler(self):
        """Thread function that processes the incoming modem data."""
        # Handle incoming calls
        call_record = {}
        text_index = 0
        while 1:
            modem_data = ""

            self._lock.acquire()
            try:
                if self.config["TESTING"]:
                    if text_index >= len(TEST_DATA):
                        break
                    modem_data = TEST_DATA[text_index]
                    text_index += 1
                else:
                    modem_data = self._serial.readline()
            finally:
                self._lock.release()

            if modem_data != "":
                if self.config["DEBUG"]:
                    pprint(modem_data)

                if "RING" in modem_data.strip(DLE_CODE):
                    self.phone_ringing(True)

                if ("DATE" in modem_data):
                    call_record['DATE'] = (modem_data[5:]).strip(' \t\n\r')
                if ("TIME" in modem_data):
                    call_record['TIME'] = (modem_data[5:]).strip(' \t\n\r')
                if ("NAME" in modem_data):
                    call_record['NAME'] = (modem_data[5:]).strip(' \t\n\r')
                if ("NMBR" in modem_data):
                    call_record['NMBR'] = (modem_data[5:]).strip(' \t\n\r')

                # https://stackoverflow.com/questions/1285911/how-do-i-check-that-multiple-keys-are-in-a-dict-in-a-single-pass
                if all(k in call_record for k in ("DATE", "TIME", "NAME", "NMBR")):
                    print "Screening call..."
                    # print call_record
                    self.handle_caller(call_record)
                    call_record = {}
                    # Sleep for a short duration to allow call attendant
                    # to screen call before resuming
                    time.sleep(2)

    def hang_up(self):
        """Terminate an active call, e.g., hang up."""
        print "Terminating call..."
        self._serial.cancel_read()
        self._lock.acquire()
        try:
            if not self._send(TERMINATE_CALL):
                print "Error: Failed to terminate the call."
        finally:
            self._lock.release()

    def block_call(self):
        """Block the current caller by answering and hanging up"""
        print "Blocking call..."
        blocked = self.config.get_namespace("BLOCKED_")
        self._serial.cancel_read()
        self._lock.acquire()
        try:
            if self._send(GO_OFF_HOOK):
                time.sleep(2)
                if "play_message" in blocked["actions"]:
                    blocked_message_file = os.path.join(
                        self.config["ROOT_PATH"],
                        blocked["message_file"])
                    self.play_audio(blocked_message_file)
                time.sleep(2)
                self._send(GO_ON_HOOK)
            else:
                print "Error: Failed to block the call."
        finally:
            self._lock.release()

    def play_audio(self, audio_file_name):
        """Play an audio file with 8-bit linear compression at 8.0 kHz sampling"""
        print "Play Audio Msg - Start"

        self._serial.cancel_read()
        self._lock.acquire()
        try:
            if not self._send(ENTER_VOICE_MODE):
                print "Error: Failed to put modem into voice mode."
                return
            if not self._send(SET_VOICE_COMPRESSION_METHOD):
                print "Error: Failed to set compression method and sampling rate specifications."
                return
            if not self._send(ENTER_TELEPHONE_ANSWERING_DEVICE_MODE):
                print "Error: Unable put modem into TAD mode."
                return
            if not self._send(ENTER_VOICE_TRANSMIT_DATA_STATE, "CONNECT"):
                print "Error: Unable put modem into TAD data transmit state."
                return

            time.sleep(1)

            # Play Audio File
            print "Play Audio Msg - playing wav file"

            wf = wave.open(audio_file_name, 'rb')
            chunk = 1024

            data = wf.readframes(chunk)
            while data != '':
                self._serial.write(data)
                data = wf.readframes(chunk)
                # You may need to change this sleep interval to smooth-out the audio
                time.sleep(.12)
            wf.close()

            # self._serial.flushInput()
            # self._serial.flushOutput()

            self._send(END_VOICE_TRANSMIT_DATA_STATE)

        finally:
            self._lock.release()

        print "Play Audio Msg - END"

    def record_audio(self, audio_file_name):
        print "Record Audio Msg - Start"

        self._serial.cancel_read()
        self._lock.acquire()
        try:
            try:
                if not self._send("AT+FCLASS=8", "OK"):
                    raise RuntimeError("Failed to put modem into voice mode.")

                if not self._send("AT+VGT=128", "OK"):
                    raise RuntimeError("Failed to set speaker volume to normal.")

                # Compression Method: 8-bit linear / Sampling Rate: 8000MHz
                if not self._send("AT+VSM=128,8000", "OK"):
                    raise RuntimeError("Failed to set compression method and sampling rate specifications.")

                if not self._send("AT+VSD=128,0", "OK"):
                    raise RuntimeError("Failed to disable silence detection.")

                if not self._send("AT+VLS=1", "OK"):
                    raise RuntimeError("Unable put modem into TAD mode.")

                # Select normal silence detection sensitivity and detection interval of 5 s.
                if not self._send("AT+VSD=128,50", "OK"):
                    raise RuntimeError("Failed to enable silence detection.")

                if not self._send("AT+VTS=[933,900,100]", "OK"):
                    raise RuntimeError("Failed to play 1.2 second beep.")

                if not self._send("AT+VRX", "CONNECT"):
                    raise RuntimeError("Error: Unable put modem into voice receive mode.")

            except RuntimeError as error:
                print "Modem initialization error: ", error
                return

            # Record Audio File

            # Set the auto timeout interval
            start_time = datetime.now()
            CHUNK = 1024
            audio_frames = []

            while 1:
                # Read audio data from the Modem
                audio_data = self._serial.read(CHUNK)

                # Check if <DLE>b is in the stream
                if ((chr(16) + chr(98)) in audio_data):
                    print "Busy Tone... Call will be disconnected."
                    break

                # Check if <DLE>s is in the stream
                if ((chr(16) + chr(115)) in audio_data):
                    print "Silence Detected... Call will be disconnected."
                    break

                # Check if <DLE><ETX> is in the stream
                if (("<DLE><ETX>").encode() in audio_data):
                    print "<DLE><ETX> Char Recieved... Call will be disconnected."
                    break

                # Timeout
                elif ((datetime.now() - start_time).seconds) > REC_VM_MAX_DURATION:
                    print "Timeout - Max recording limit reached."
                    break

                # Add Audio Data to Audio Buffer
                audio_frames.append(audio_data)

            # Save the Audio into a .wav file
            wf = wave.open(audio_file_name, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(1)
            wf.setframerate(8000)
            wf.writeframes(b''.join(audio_frames))
            wf.close()

            # Reset Audio File Name
            audio_file_name = ''

            # Send End of Voice Recieve state by passing "<DLE>!"
            if not self._send((chr(16) + chr(33)), "OK"):
                print "Error: Unable to signal end of voice receive state"

            # Hangup the Call
            if not self._send("ATH", "OK"):
                print "Error: Unable to hang-up the call"

        finally:
            self._lock.release()

        print "Record Audio Msg - END"
        return

    def _send(self, command, expected_response=None, response_timeout=5):
        """Sends a command string (e.g., AT command) to the modem."""

        # Disable processing while sending commands lest the response
        # get processed by the event processing thread.
        self._lock.acquire()

        try:
            self._serial.write((command + "\r").encode())
            if expected_response is None:
                return True
            else:
                execution_status = self._read_response(expected_response, response_timeout)
                return execution_status
        except:
            print "Error: Failed to execute the command"
            return False

        finally:
            # Resume event processing
            self._lock.release()

    def _read_response(self, expected_response, response_timeout_secs):
        """
        Handles the command response code from the modem.
        Returns True if the expected response was returned.
        Returns False if ERROR is returned or if it times out
        before the expected response is returned
        """
        start_time = datetime.now()
        try:
            while 1:
                modem_data = self._serial.readline()
                print modem_data
                response = modem_data.strip(' \t\n\r' + DLE_CODE)
                if expected_response == response:
                    return True
                elif "ERROR" in response:
                    return False
                elif (datetime.now() - start_time).seconds > response_timeout_secs:
                    return False
        except:
            print "Error in read_response function..."
            return False

    def _init_modem(self):
        """Auto-detects and initializes the modem."""
        # Detect and open the Modem Serial COM Port
        try:
            self.open_serial_port()
        except:
            print "Error: Unable to open the Serial Port."
            sys.exit()

        # Initialize the Modem
        try:
            # Flush any existing input outout data from the buffers
            self._serial.flushInput()
            self._serial.flushOutput()

            # Test Modem connection, using basic AT command.
            if not self._send("AT", "OK"):
                print "Error: Unable to access the Modem"
            if not self._send(FACTORY_RESET, "OK"):
                print "Error: Unable reset to factory default"
            if not self._send(ENABLE_VERBOSE_CODES, "OK"):
                print "Error: Unable set response in verbose form"
            if not self._send(ENABLE_ECHO_COMMANDS, "OK"):
                print "Error: Failed to enable local echo mode"
            if not self._send(ENABLE_FORMATTED_CID, "OK"):
                print "Error: Failed to enable formatted caller report."

            self._send(DISPLAY_MODEM_SETTINGS)

            # Flush any existing input outout data from the buffers
            self._serial.flushInput()
            self._serial.flushOutput()

            # Automatically close the serial port at program termination
            atexit.register(self.close_serial_port)

        except:
            print "Error: unable to Initialize the Modem"
            sys.exit()

    def open_serial_port(self):
        """Detects and opens the serial port attached to the modem."""
        # List all the Serial COM Ports on Raspberry Pi
        proc = subprocess.Popen(['ls /dev/tty[A-Za-z]*'], shell=True, stdout=subprocess.PIPE)
        com_ports = proc.communicate()[0]
        com_ports_list = com_ports.split('\n')

        # Find the right port associated with the Voice Modem
        for com_port in com_ports_list:
            if 'tty' in com_port:
                # Try to open the COM Port and execute AT Command
                try:
                    # Initialize the serial port and attempt to open
                    self._init_serial_port(com_port)
                    self._serial.open()
                except:
                    print "Unable to open COM Port: " + com_port
                    pass
                else:
                    # Validate modem selection by trying to put it in Voice Mode
                    if not self._send(ENTER_VOICE_MODE, "OK"):
                        print "Error: Failed to put modem into voice mode."
                        if self._serial.isOpen():
                            self._serial.close()
                    else:
                        # Found the COM Port exit the loop
                        print "Modem COM Port is: " + com_port
                        self._serial.flushInput()
                        self._serial.flushOutput()
                        break

    def _init_serial_port(self, com_port):
        """Initializes the given COM port for communications with the modem."""
        self._serial.port = com_port
        self._serial.baudrate = 57600  # 9600
        self._serial.bytesize = serial.EIGHTBITS  # number of bits per bytes
        self._serial.parity = serial.PARITY_NONE  # set parity check: no parity
        self._serial.stopbits = serial.STOPBITS_ONE  # number of stop bits
        self._serial.timeout = 3  # non-block read
        self._serial.xonxoff = False  # disable software flow control
        self._serial.rtscts = False  # disable hardware (RTS/CTS) flow control
        self._serial.dsrdtr = False  # disable hardware (DSR/DTR) flow control
        self._serial.writeTimeout = 3  # timeout for write

    def close_serial_port(self):
        """Closes the serial port attached to the modem."""
        print("Closing Serial Port")
        try:
            if self._serial.isOpen():
                self._serial.close()
                print("Serial Port closed...")
        except:
            print "Error: Unable to close the Serial Port."
            sys.exit()


def test(config, phone_ringing, handle_caller):
    """ Unit Tests """
    import os

    print("Running Unit Tests....")
    modem = Modem(config, phone_ringing, handle_caller)

    try:
        modem.open_serial_port()
    except:
        print("Error: Unable to open the Serial Port.")
        return 1

    print("Assert factory reset")
    assert modem._send(FACTORY_RESET, "OK")

    print("Assert display modem settings")
    assert modem._send(DISPLAY_MODEM_SETTINGS, "OK")

    print("Assert put modem into voice mode.")
    assert modem._send(ENTER_VOICE_MODE, "OK")

    print("Assert set compression method and sampling rate specifications.")
    assert modem._send(SET_VOICE_COMPRESSION_METHOD, "OK")

    print("Assert put modem into TAD mode.")
    assert modem._send(ENTER_TELEPHONE_ANSWERING_DEVICE_MODE, "OK")

    print("Assert put modem into data transmit state.")
    assert modem._send(ENTER_VOICE_TRANSMIT_DATA_STATE, "CONNECT")

    print("Assert cancel data transmit state.")
    assert modem._send(END_VOICE_TRANSMIT_DATA_STATE, "OK")

    modem._send(FACTORY_RESET)

    currentdir = os.path.dirname(os.path.realpath(__file__))
    modem.play_audio(os.path.join(currentdir, "sample.wav"))

    modem.record_audio("message.wav")

    return 0


if __name__ == '__main__':
    """ Run the Unit Tests """

    # Add the parent directory to the path so callattendant can be found
    import os, sys
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)

    # Load and tweak the default config
    from callattendant import make_config, print_config
    config = make_config()
    config['DEBUG'] = True
    print_config(config)

    # Dummy callback functions
    phone_ringing = lambda is_ringing : pprint(is_ringing)
    handle_caller = lambda caller : pprint(caller)

    # Run the tests
    sys.exit(test(config, phone_ringing, handle_caller))
    print("Done")
