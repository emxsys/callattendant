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
import re
import serial
import subprocess
import sys
import threading
import time
import wave


# ACSII codes
DLE_CODE = chr(16)      # Data Link Escape (DLE) code
ETX_CODE = chr(3)       # End Transmission (ETX) code

#  Modem AT commands:
#  See http://support.usr.com/support/5637/5637-ug/ref_data.html
FACTORY_RESET = "ATZ3"
DISPLAY_MODEM_SETTINGS = "ATI4"
ENABLE_ECHO_COMMANDS = "ATE1"
ENABLE_FORMATTED_CID = "AT+VCID=1"
ENABLE_VERBOSE_CODES = "ATV1"
ENABLE_SILENCE_DETECTION_5_SECS = "AT+VSD=128,50"
ENABLE_SILENCE_DETECTION_10_SECS = "AT+VSD=128,100"
ENTER_VOICE_MODE = "AT+FCLASS=8"
ENTER_TELEPHONE_ANSWERING_DEVICE_MODE = "AT+VLS=1"  # DCE off-hook
ENTER_VOICE_TRANSMIT_DATA_STATE = "AT+VTX"
ENTER_VOICE_RECIEVE_DATA_STATE = "AT+VRX"
END_VOICE_TRANSMIT_DATA_STATE = DLE_CODE + ETX_CODE
SET_VOICE_COMPRESSION_METHOD = "AT+VSM=128,8000"  # 128 = 8-bit linear, 8.0 kHz
GO_OFF_HOOK = "ATH1"
GO_ON_HOOK = "ATH0"
TERMINATE_CALL = "ATH"

# Modem DLE shielded codes - DCE to DTE
DCE_ANSWER_TONE = (chr(16) + chr(97)).encode()          # <DLE>-a
DCE_BUSY_TONE = (chr(16) + chr(98)).encode()            # <DLE>-b
DCE_FAX_CALLING_TONE = (chr(16) + chr(99)).encode()     # <DLE>-c
DCE_DIAL_TONE = (chr(16) + chr(100)).encode()           # <DLE>-d
DCE_DATA_CALLING_TONE = (chr(16) + chr(101)).encode()   # <DLE>-e
DCE_PHONE_ON_HOOK = (chr(16) + chr(104)).encode()       # <DLE>-h
DCE_PHONE_OFF_HOOK = (chr(16) + chr(72)).encode()       # <DLE>-H
DCE_RING = (chr(16) + chr(82)).encode()                 # <DLE>-R
DCE_SILENCE_DETECTED = (chr(16) + chr(115)).encode()    # <DLE>-s
DCE_END_VOICE_DATA_TX = (chr(16) + chr(3)).encode()     # <DLE><ETX>

# System DLE shielded codes - DTE to DCE
DTE_RAISE_VOLUME = (chr(16) + chr(117))                 # <DLE>-u
DTE_LOWER_VOLUME = (chr(16) + chr(100))                 # <DLE>-d
DTE_END_VOICE_DATA_TX = (chr(16) + chr(3))              # <DLE><ETX>
DTE_END_RECIEVE_DATA_STATE = (chr(16) + chr(33))        # <DLE>-!

# Record Voice Mail variables
REC_VM_MAX_DURATION = 120  # Time in Seconds

TEST_DATA = [
    b"RING", b"DATE=0801", b"TIME=1800", b"NMBR=5551234567", b"NAME=Test1 - Spammer",
    b"RING", b"DATE=0801", b"TIME=1801", b"NMBR=8055554567", b"NAME=Test2 - Permitted",
    b"RING", b"DATE=0801", b"TIME=1802", b"NMBR=3605554567", b"NAME=Test3 - Blocked",
    b"RING", b"DATE=0801", b"TIME=1802", b"NMBR=3605554567", b"NAME=V123456789012345",
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
            :param phone_ringing: callback function that takes a boolean
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
        self.event_thread.name = "modem_call_handler"
        self.event_thread.start()

    def _call_handler(self):
        """
        Thread function that processes the incoming modem data.
        """

        # Handle incoming calls
        call_record = {}
        text_index = 0

        debugging = self.config["DEBUG"]
        testing = self.config["TESTING"]
        logging = False
        logfile = None
        # Save the modem data to a file for development purposes
        if self.config["ENV"] == "development":
            print("Saving raw modem data to modem.log")
            logfile = open("modem.log", 'wb')
            logging = True

        try:
            # This loop reads incoming data from the serial port and
            # posts the caller id data to the handle_caller function
            while 1:
                modem_data = b''

                self._lock.acquire()
                try:
                    if testing:
                        # Iterate thru the test data
                        if text_index >= len(TEST_DATA):
                            break
                        modem_data = TEST_DATA[text_index]
                        text_index += 1
                    else:
                        # Read a line of data from the serial port
                        modem_data = self._serial.readline()
                finally:
                    self._lock.release()

                if modem_data != b'':
                    if debugging:
                        print(modem_data)

                    if logging:
                        logfile.write(modem_data)
                        logfile.flush()

                    if "RING".encode("utf-8") in modem_data.strip(DLE_CODE.encode("utf-8")):
                        self.phone_ringing(True)
                    if ("DATE".encode("utf-8") in modem_data):
                        call_record['DATE'] = decode(modem_data[5:])
                    if ("TIME".encode("utf-8")in modem_data):
                        call_record['TIME'] = decode(modem_data[5:])
                    if ("NAME".encode("utf-8") in modem_data):
                        call_record['NAME'] = decode(modem_data[5:])
                    if ("NMBR".encode("utf-8") in modem_data):
                        call_record['NMBR'] = decode(modem_data[5:])

                    # https://stackoverflow.com/questions/1285911/how-do-i-check-that-multiple-keys-are-in-a-dict-in-a-single-pass
                    if all(k in call_record for k in ("DATE", "TIME", "NAME", "NMBR")):
                        print("> Screening call...")
                        self.handle_caller(call_record)
                        call_record = {}
                        # Sleep for a short duration ( secs) to allow the
                        # call attendant to screen the call before resuming
                        time.sleep(2)
        finally:
            if logging:
                print("Closing modem log file")
                logfile.close()

    def pick_up(self):
        """
        Go "off hook". Called by the application object (callattendant.py)
        to set the lock and perform a batch of operations before hanging up.
        The hang_up() function must be called to release the lock.

        note:: hang_up MUST be called by the same thread to release the lock
        """
        print("> Going off hook...")
        self._serial.cancel_read()
        self._lock.acquire()
        try:
            if not self._send(GO_OFF_HOOK):
                print("Error: Failed to pickup.")
                return False
        except Exception as e:
            pprint(e)
            self._lock.release()
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
            if not self._send(GO_ON_HOOK):
                print("Error: Failed to terminate the call.")
                return False
        finally:
            self._lock.release()
        return True

    def block_call(self, caller=None):
        """ Block the current caller by answering and hanging up """
        print("> Blocking call...")
        blocked = self.config.get_namespace("BLOCKED_")
        self._serial.cancel_read()
        self._lock.acquire()
        try:
            if self._send(GO_OFF_HOOK):
                time.sleep(2)
                if "play_greeting" in blocked["actions"]:
                    blocked_message_file = os.path.join(
                        self.config["ROOT_PATH"],
                        blocked["greeting_file"])
                    self.play_audio(blocked_message_file)
                if "record_message" in blocked["actions"]:
                    time.sleep(1)
                    leave_message_file = os.path.join(
                        self.config["ROOT_PATH"],
                        blocked["leave_message_file"])
                    self.play_audio(leave_message_file)
                    if blocked["leave_message_action"] == "leave_message":
                        filename = "{}-{}.wav".format(
                            caller["NMBR"],
                            datetime.now().strftime("%Y%m%d-%H%M%S"))
                        path = os.path.join(
                            self.config["ROOT_PATH"],
                            self.config["MESSAGE_FOLDER"])
                        if not os.path.exists(path):
                            os.makedirs('my_folder')
                        message_file = os.path.join(path, filename)
                        self.record_audio(message_file)
                    elif blocked["leave_message_action"] == "press_1_leave_message":
                        pass
                time.sleep(2)
                self._send(GO_ON_HOOK)
            else:
                print("Error: Failed to block the call.")
        finally:
            self._lock.release()

    def play_audio(self, audio_file_name):
        """
        Play the given audio file.
            :param audio_file_name: a wav file with 8-bit linear
                compression recored at 8.0 kHz sampling rate
        """
        print("> Playing {}...".format(audio_file_name))

        self._serial.cancel_read()
        self._lock.acquire()
        try:
            # Setup modem for transmitting audio data
            if not self._send(ENTER_VOICE_MODE):
                print("* Error: Failed to put modem into voice mode.")
                return False
            if not self._send(SET_VOICE_COMPRESSION_METHOD):
                print("* Error: Failed to set compression method and sampling rate specifications.")
                return False
            if not self._send(ENTER_TELEPHONE_ANSWERING_DEVICE_MODE):
                print("* Error: Unable put modem into TAD mode.")
                return False
            if not self._send(ENTER_VOICE_TRANSMIT_DATA_STATE, "CONNECT"):
                print("* Error: Unable put modem into TAD data transmit state.")
                return False

            # Play Audio File
            wf = wave.open(audio_file_name, 'rb')
            chunk = 1024

            data = wf.readframes(chunk)
            while data != b'':
                self._serial.write(data)
                data = wf.readframes(chunk)
                # You may need to change this sleep interval to smooth-out the audio
                time.sleep(.12)  # 120ms
            wf.close()

            # self._serial.flushInput()
            # self._serial.flushOutput()

            self._send(END_VOICE_TRANSMIT_DATA_STATE, "OK")

        finally:
            self._lock.release()

        return True

    def record_audio(self, audio_file_name):
        """
        Records audio from the model to the given audio file.
            :param audio_file_name: the wav file to be created with the
                recorded audio; recored with 8-bit linear compression
                at 8.0 kHz sampling rate
        """
        print("> Recording {}...".format(audio_file_name))

        self._serial.cancel_read()
        self._lock.acquire()

        debugging = self.config["DEBUG"]
        try:
            try:
                if not self._send(ENTER_VOICE_MODE, "OK"):
                    raise RuntimeError("Failed to put modem into voice mode.")

                if not self._send("AT+VGT=128", "OK"):
                    raise RuntimeError("Failed to set speaker volume to normal.")

                # Compression Method: 8-bit linear / Sampling Rate: 8000MHz
                if not self._send("AT+VSM=128,8000", "OK"):
                    raise RuntimeError("Failed to set compression method and sampling rate specifications.")

                if not self._send("AT+VSD=128,0", "OK"):
                    raise RuntimeError("Failed to disable silence detection.")

                if not self._send(ENTER_TELEPHONE_ANSWERING_DEVICE_MODE, "OK"):
                    raise RuntimeError("Unable put modem into TAD mode.")

                # Play 1.2 beep
                if not self._send("AT+VTS=[933,900,120]", "OK"):
                    raise RuntimeError("Failed to play 1.2 second beep.")

                # Select normal silence detection sensitivity and detection interval of 5 s.
                if not self._send("AT+VSD=128,50", "OK"):
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

                # Check if <DLE>b is in the stream
                if (DCE_BUSY_TONE in audio_data):
                    print(">> Busy Tone... Call will be disconnected.")
                    break

                # Check if <DLE>s is in the stream
                if (DCE_SILENCE_DETECTED in audio_data):
                    print(">> Silence Detected... Call will be disconnected.")
                    break

                # Check if <DLE><ETX> is in the stream
                if (DCE_END_VOICE_DATA_TX in audio_data):
                    print(">> <DLE><ETX> Char Recieved... Call will be disconnected.")
                    break

                # Timeout
                elif ((datetime.now() - start_time).seconds) > REC_VM_MAX_DURATION:
                    print(">> Timeout - Max recording limit reached.")
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

            # Clear buffer before sending commands
            self._serial.reset_input_buffer()

            # Send End of Recieve Data state by passing "<DLE>!"
            if not self._send(DTE_END_RECIEVE_DATA_STATE, DLE_CODE + ETX_CODE):
                print("* Error: Unable to signal end of voice/data receive state")

            # Hangup the Call
            # if not self._send(TERMINATE_CALL, "OK"):
            #     print("* Error: Unable to hang-up the call")

        finally:
            self._lock.release()

        return True

    def wait_for_keypress(self, seconds=5):
        """
        Waits n seconds for a keypress.
            :params seconds: the number of seconds to wait for a keypress
            :return: the keypress
        """
        print("> Waiting for keypress...")

        self._serial.cancel_read()
        self._lock.acquire()

        debugging = self.config["DEBUG"]
        try:
            modem_data = b''
            try:
                if not self._send(ENTER_VOICE_MODE, "OK"):
                    raise RuntimeError("Failed to put modem into voice mode.")

                if not self._send(ENABLE_SILENCE_DETECTION_10_SECS, "OK"):
                    raise RuntimeError("Failed to enable silence detection.")

                if not self._send(ENTER_TELEPHONE_ANSWERING_DEVICE_MODE, "OK"):
                    raise RuntimeError("Unable put modem into TAD mode.")

            except RuntimeError as error:
                print("Modem initialization error: ", error)
                return ''


            # Wait for keypress
            start_time = datetime.now()
            while 1:
                # Read 1 bytes from the Modem
                modem_data = modem_data + self._serial.read(1)
                print("modem_data:")
                pprint(modem_data)

                # Check if <DLE>h is in the stream
                if (DCE_PHONE_ON_HOOK in modem_data):
                    print(">> Phone On Hook... Aborting")
                    break

                # Check if <DLE>b is in the stream
                if (DCE_BUSY_TONE in modem_data):
                    print(">> Busy Tone... Aborting wait for key.")
                    break

                # Check if <DLE>s is in the stream
                if (DCE_SILENCE_DETECTED in modem_data):
                    print(">> Silence Detected... Aborting wait for key.")
                    break

                # Check if <DLE><ETX> is in the stream
                if (DCE_END_VOICE_DATA_TX in modem_data):
                    print(">> <DLE><ETX> Char Recieved... Aboring.")
                    break

                # Parse DTMF Digits, if found in the modem data
                digit_list = re.findall('/(.+?)~', decode(modem_data))
                if len(digit_list) > 0:
                    print("Digits:")
                    pprint(digit_list)
                    for d in digit_list:
                        print("\nNew Event: DTMF Digit Detected: " + d[1])
                        return d[1]
        finally:
            self._lock.release()

        return ''

    def _send(self, command, expected_response=None, response_timeout=5):
        """
        Sends a command string (e.g., AT command) to the modem.
            :param command: the command string to send
            :param expected response: the expected response to the command, e.g. "OK"
            :param response_timeout: number of seconds to wait for the command to respond
            :return: True if the command response matches the expected_response
        """
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
        except Exception as e:
            print(e)
            print("Error: Failed to execute the command")
            return False

        finally:
            # Resume event processing
            self._lock.release()

    def _read_response(self, expected_response, response_timeout_secs):
        """
        Handles the command response code from the modem.
        before the expected response is returned
            :param expected response: the expected response, e.g. "OK"
            :param response_timeout_secs: number of seconds to wait for
                the command to respond
            :return: True if the response matches the expected_response;
                False if ERROR is returned or if it times out
        """

        start_time = datetime.now()
        try:
            while 1:
                modem_data = self._serial.readline()
                response = modem_data.decode("utf-8").strip(' \t\n\r')  # strip DLE_CODE too?
                if expected_response == response:
                    return True
                elif "ERROR" in response:
                    return False
                elif (datetime.now() - start_time).seconds > response_timeout_secs:
                    return False
        except Exception as e:
            print(e)
            print("Error in read_response function...")
            return False

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
            if not self._send("AT", "OK"):
                print("Error: Unable to access the Modem")
            if not self._send(FACTORY_RESET, "OK"):
                print("Error: Unable reset to factory default")
            if not self._send(ENABLE_VERBOSE_CODES, "OK"):
                print("Error: Unable set response in verbose form")
            if not self._send(ENABLE_ECHO_COMMANDS, "OK"):
                print("Error: Failed to enable local echo mode")
            if not self._send(ENABLE_FORMATTED_CID, "OK"):
                print("Error: Failed to enable formatted caller report.")

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

    def open_serial_port(self):
        """Detects and opens the serial port attached to the modem."""
        # List all the Serial COM Ports on Raspberry Pi
        proc = subprocess.Popen(['ls /dev/tty[A-Za-z]*'], shell=True, stdout=subprocess.PIPE)
        com_ports = proc.communicate()[0]
        # In order to split, need to pass a bytes-like object
        com_ports_list = com_ports.split(b'\n')

        # Find the right port associated with the Voice Modem
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
                    # Validate modem selection by trying to put it in Voice Mode
                    if not self._send(ENTER_VOICE_MODE, "OK"):
                        print("Error: Failed to put modem into voice mode.")
                        if self._serial.isOpen():
                            self._serial.close()
                    else:
                        # Found the COM Port exit the loop
                        print("Modem COM Port is: " + com_port.decode("utf-8"))
                        self._serial.flushInput()
                        self._serial.flushOutput()
                        break

    def _init_serial_port(self, com_port):
        """Initializes the given COM port for communications with the modem."""
        self._serial.port = com_port
        self._serial.baudrate = 57600               # 9600
        self._serial.bytesize = serial.EIGHTBITS    # number of bits per bytes
        self._serial.parity = serial.PARITY_NONE    # set parity check: no parity
        self._serial.stopbits = serial.STOPBITS_ONE # number of stop bits
        self._serial.timeout = 3                    # non-block read
        self._serial.xonxoff = False                # disable software flow control
        self._serial.rtscts = False                 # disable hardware (RTS/CTS) flow control
        self._serial.dsrdtr = False                 # disable hardware (DSR/DTR) flow control
        self._serial.writeTimeout = 3               # timeout for write

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
    string = bytestr.decode("utf-8").strip(' \t\n\r')
    return string


def test(config, phone_ringing, handle_caller):
    """ Unit Tests """
    import os

    print("*** Running Modem Unit Tests ***")

    modem = Modem(config, phone_ringing, handle_caller)

    try:
        modem.open_serial_port()
    except Exception as e:
        print(e)
        print("Error: Unable to open the Serial Port.")
        return 1

    try:
        print("Assert factory reset")
        assert modem._send(FACTORY_RESET, "OK"), "FACTORY_RESET"

        print("Assert display modem settings")
        assert modem._send(DISPLAY_MODEM_SETTINGS, "OK"), "DISPLAY_MODEM_SETTINGS"

        print("Assert put modem into voice mode.")
        assert modem._send(ENTER_VOICE_MODE, "OK"), "ENTER_VOICE_MODE"

        print("Assert set compression method and sampling rate specifications.")
        assert modem._send(SET_VOICE_COMPRESSION_METHOD, "OK"), "SET_VOICE_COMPRESSION_METHOD"

        print("Assert put modem into TAD mode.")
        assert modem._send(ENTER_TELEPHONE_ANSWERING_DEVICE_MODE, "OK"), "ENTER_TELEPHONE_ANSWERING_DEVICE_MODE"

        print("Assert put modem into data transmit state.")
        assert modem._send(ENTER_VOICE_TRANSMIT_DATA_STATE, "CONNECT"), "ENTER_VOICE_TRANSMIT_DATA_STATE"

        print("Assert cancel data transmit state.")
        assert modem._send(END_VOICE_TRANSMIT_DATA_STATE, "OK"), "END_VOICE_TRANSMIT_DATA_STATE"

        # Test audio play/recording when functional testing is enabled
        if config["TESTING"]:
            modem._send(FACTORY_RESET)

            currentdir = os.path.dirname(os.path.realpath(__file__))
            modem.play_audio(os.path.join(currentdir, "sample.wav"))
            modem._send(TERMINATE_CALL, "OK")

            modem._send(FACTORY_RESET)
            modem.record_audio("message.wav")

    except Exception as e:
        print("*** Unit test FAILED ***")
        pprint(e)
        return 1

    print("*** Unit tests PASSED ***")
    return 0


if __name__ == '__main__':
    """ Run the Unit Tests """

    # Add the parent directory to the path so callattendant can be found
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)
    sys.path.append(os.path.join(parentdir, "screening"))

    # Load and tweak the default config
    from callattendant import make_config, print_config
    config = make_config()
    config['DEBUG'] = True
    config['TESTING'] = True
    print_config(config)

    # Dummy callback functions
    def dummy_phone_ringing(is_ringing):
        print(is_ringing)

    def dummy_handle_caller(caller):
        pprint(caller)

    # Run the tests
    sys.exit(test(config, dummy_phone_ringing, dummy_handle_caller))
