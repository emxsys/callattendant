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
import atexit
import serial
import subprocess
import sys
import threading
import time
import wave

#  Modem AT commands:
#  See http://support.usr.com/support/5637/5637-ug/ref_data.html
DLE_CODE = chr(16)  # Data Link Escape code
ETX_CODE = chr(3)  # End Transmission code
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


class Modem(object):
    """
    This class is responsible for serial communications between the
    Raspberry Pi and a US Robotics 5637 modem.
    """

    def __init__(self, call_attendant):
        """Constructs a modem object for serial communications."""
        self.call_attendant = call_attendant
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

        # Prerequisites
        if self.call_attendant == None:
            print "No call attendant in call handler; calls will not be handled."
            return

        # Handle incoming calls
        call_record = {}
        while 1:
            modem_data = ""

            self._lock.acquire()
            try:
                modem_data = self._serial.readline()
            finally:
                self._lock.release()

            if modem_data != "":
                print modem_data

                if "RING" in modem_data.strip(DLE_CODE):
                    self.call_attendant.phone_ringing(True)

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
                    self.call_attendant.handler_caller(call_record)
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
            if not self._send_cmd(TERMINATE_CALL):
                print "Error: Failed to terminate the call."
        finally:
            self._lock.release()

    def block_call(self):
        """Block the current caller by answering and hanging up"""
        print "Blocking call..."
        self._serial.cancel_read()
        self._lock.acquire()
        try:
            if self._send_cmd(GO_OFF_HOOK):
                time.sleep(2)
                self._send_cmd(GO_ON_HOOK)
            else:
                print "Error: Failed to block the call."
        finally:
            self._lock.release()

    def play_audio(self, wave_filename):
        """Play an audio file with 8-bit linear compression at 8.0 kHz sampling"""
        print "Play Audio Msg - Start"

        self._serial.cancel_read()
        self._lock.acquire()
        try:
            if not self._send_cmd(ENTER_VOICE_MODE):
                print "Error: Failed to put modem into voice mode."
                return
            if not self._send_cmd(SET_VOICE_COMPRESSION_METHOD):
                print "Error: Failed to set compression method and sampling rate specifications."
                return
            if not self._send_cmd(ENTER_TELEPHONE_ANSWERING_DEVICE_MODE):
                print "Error: Unable put modem into TAD mode."
                return
            if not self._send_cmd(ENTER_VOICE_TRANSMIT_DATA_STATE, "CONNECT"):
                print "Error: Unable put modem into TAD data transmit state."
                return

            time.sleep(1)

            # Play Audio File
            print "Play Audio Msg - playing wav file"

            wf = wave.open(wave_filename, 'rb')
            chunk = 1024

            data = wf.readframes(chunk)
            while data != '':
                self._serial.write(data)
                data = wf.readframes(chunk)
                # You may need to change this sleep interval to smooth-out the audio
                time.sleep(.12)
            wf.close()

            #self._serial.flushInput()
            #self._serial.flushOutput()

            self._send_cmd(END_VOICE_TRANSMIT_DATA_STATE, "NONE")
            #self._send_cmd(TERMINATE_CALL)

        finally:
            self._lock.release()

        print "Play Audio Msg - END"

    def _send_cmd(self, command, expected_response="OK"):
        """Sends a command string (e.g., AT command) to the modem."""
        # Disable processing while sending commands lest the response
        # get processed by the event processing thread.
        self._lock.acquire()
        try:
            self._serial.write((command + "\r").encode())
            if expected_response == "NONE" or expected_response == "":
                return True
            else:
                execution_status = self._read_response(expected_response)
                return execution_status
        except:
            print "Error: Failed to execute the command"
            return False
        finally:
            # Resume event processing
            self._lock.release()

    def _read_response(self, expected_response="OK", read_timeout_secs=5):
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
                elif (datetime.now() - start_time).seconds > read_timeout_secs:
                    return False
        except:
            print "Error in read_cmd_modem_response function..."
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
            if not self._send_cmd("AT"):
                print "Error: Unable to access the Modem"
            if not self._send_cmd(FACTORY_RESET):
                print "Error: Unable reset to factory default"
            if not self._send_cmd(ENABLE_VERBOSE_CODES):
                print "Error: Unable set response in verbose form"
            if not self._send_cmd(ENABLE_ECHO_COMMANDS):
                print "Error: Failed to enable local echo mode"
            if not self._send_cmd(ENABLE_FORMATTED_CID):
                print "Error: Failed to enable formatted caller report."
            if not self._send_cmd(DISPLAY_MODEM_SETTINGS):
                print "Error: Failed to display modem settings."

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
                    self.init_serial_port(com_port)
                    self._serial.open()
                except:
                    print "Unable to open COM Port: " + com_port
                    pass
                else:
                    # Validate modem selection by trying to put it in Voice Mode
                    if not self._send_cmd(ENTER_VOICE_MODE):
                        print "Error: Failed to put modem into voice mode."
                        if self._serial.isOpen():
                            self._serial.close()
                    else:
                        # Found the COM Port exit the loop
                        print "Modem COM Port is: " + com_port
                        self._serial.flushInput()
                        self._serial.flushOutput()
                        break

    def init_serial_port(self, com_port):
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

def test(args):

    print "Running tests...."
    modem = Modem(None) # No call attendent is set in tests

    try:
        modem.open_serial_port()
    except:
        print "Error: Unable to open the Serial Port."
        return 1

    if not modem._send_cmd(FACTORY_RESET, "OK"):
        print "Factory reset failed."
    if not modem._send_cmd(DISPLAY_MODEM_SETTINGS, "OK"):
        print "Display modem settings failed."
    if not modem._send_cmd(ENTER_VOICE_MODE):
        print "Error: Failed to put modem into voice mode."
    if not modem._send_cmd(SET_VOICE_COMPRESSION_METHOD):
        print "Error: Failed to set compression method and sampling rate specifications."
    if not modem._send_cmd(ENTER_TELEPHONE_ANSWERING_DEVICE_MODE):
        print "Error: Unable to put modem into TAD mode."
    if not modem._send_cmd(ENTER_VOICE_TRANSMIT_DATA_STATE, "CONNECT"):
        print "Error: Unable to put modem into data transmit state."
    if not modem._send_cmd(END_VOICE_TRANSMIT_DATA_STATE, "OK"):
        print "Error: Unable to cancel data transmit state."

    modem._send_cmd(FACTORY_RESET)

    modem.play_audio("sample.wav")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(test(sys.argv))
    print("Done")
