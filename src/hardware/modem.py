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

#  Modem AT commands:
#  See http://support.usr.com/support/5637/5637-ug/ref_data.html
FACTORY_RESET_CMD = "ATZ3"
PICKUP_CMD = "ATH1"
HANGUP_CMD = "ATH0"
DISPLAY_MODEM_SETTINGS_CMD = "ATI4"
ENABLE_ECHO_COMMANDS = "ATE1"
ENABLE_FORMATTED_CID = "AT+VCID=1"
ENABLE_VERBOSE_CODES = "ATV1"
ENABLE_VOICE_MODE = "AT+FCLASS=8"


class Modem(object):
    """
    This class is responsible for serial communications between the
    Raspberry Pi and a US Robotics 5637 modem.
    """

    def __init__(self, call_attendant):
        """Constructs and starts a modem for serial communications."""
        self.call_attendant = call_attendant
        # Thread synchronization objects
        self.lock = threading.RLock()
        # Setup and open the serial port
        self.read_buffer = bytearray("", encoding='ascii')
        self.serial_port = serial.Serial()
        self._init_modem()
        # Start the event processing
        self.event_thread = threading.Thread(target=self.handle_calls)
        self.event_thread.start()

    def handle_calls(self):
        """Thread function that processes the incoming modem data."""
        call_record = {}
        while 1:
            modem_data = ""

            self.lock.acquire()
            try:
                # modem_data = self._readline().decode('UTF-8')
                modem_data = self.serial_port.readline()
            finally:
                self.lock.release()

            if modem_data != "":
                print modem_data

                if "RING" in modem_data.strip(chr(16)):
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

    def block_call(self):
        """Block the current caller by answering and hanging up"""
        print "Blocking call..."
        self.serial_port.cancel_read()
        self.lock.acquire()
        try:
            if self._send_cmd(PICKUP_CMD):
                time.sleep(2)
                self._send_cmd(HANGUP_CMD)
            else:
                print "Error: Failed to block the call."
        finally:
            self.lock.release()

    def _send_cmd(self, command, expected_response="OK"):
        """Sends a command string (e.g., AT command) to the modem."""
        # Disable processing while sending commands lest the response
        # get processed by the event processing thread.
        self.lock.acquire()
        try:
            self.serial_port.write((command + "\r").encode())
            execution_status = self._read_cmd_response(expected_response)
            return execution_status
        except:
            print "Error: Failed to execute the command"
            return False
        finally:
            # Resume event processing
            self.lock.release()

    def _read_cmd_response(self, expected_response="OK"):
        """
        Handles the command response code from the modem.
        Returns True if the expected response was returned.
        """
        # Set the auto timeout interval
        MODEM_RESPONSE_READ_TIMEOUT = 5  # Time in Seconds
        start_time = datetime.now()

        try:
            while 1:
                # Read Modem Data on Serial Rx Pin
                modem_response = self.serial_port.readline()
                print modem_response
                # Received expected Response
                if expected_response == modem_response.strip(' \t\n\r' + chr(16)):
                    return True
                # Failed to execute the command successfully
                elif "ERROR" in modem_response.strip(' \t\n\r' + chr(16)):
                    return False
                # Timeout
                elif (datetime.now() - start_time).seconds > MODEM_RESPONSE_READ_TIMEOUT:
                    return False

        except:
            print "Error in read_modem_response function..."
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
            self.serial_port.flushInput()
            self.serial_port.flushOutput()

            # Test Modem connection, using basic AT command.
            if not self._send_cmd("AT"):
                print "Error: Unable to access the Modem"
            if not self._send_cmd(FACTORY_RESET_CMD):
                print "Error: Unable reset to factory default"
            if not self._send_cmd(ENABLE_VERBOSE_CODES):
                print "Error: Unable set response in verbose form"
            if not self._send_cmd(ENABLE_ECHO_COMMANDS):
                print "Error: Failed to enable local echo mode"
            if not self._send_cmd(ENABLE_FORMATTED_CID):
                print "Error: Failed to enable formatted caller report."
            if not self._send_cmd(DISPLAY_MODEM_SETTINGS_CMD):
                print "Error: Failed to display modem settings."

            # Flush any existing input outout data from the buffers
            self.serial_port.flushInput()
            self.serial_port.flushOutput()

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
                    self.serial_port.open()
                except:
                    print "Unable to open COM Port: " + com_port
                    pass
                else:
                    # Validate modem selection by trying to put it in Voice Mode
                    if not self._send_cmd(ENABLE_VOICE_MODE):
                        print "Error: Failed to put modem into voice mode."
                        if self.serial_port.isOpen():
                            self.serial_port.close()
                    else:
                        # Found the COM Port exit the loop
                        print "Modem COM Port is: " + com_port
                        self.serial_port.flushInput()
                        self.serial_port.flushOutput()
                        break

    def init_serial_port(self, com_port):
        """Initializes the given COM port for communications with the modem."""
        self.serial_port.port = com_port
        self.serial_port.baudrate = 57600  # 9600
        self.serial_port.bytesize = serial.EIGHTBITS  # number of bits per bytes
        self.serial_port.parity = serial.PARITY_NONE  # set parity check: no parity
        self.serial_port.stopbits = serial.STOPBITS_ONE  # number of stop bits
        self.serial_port.timeout = 3  # non-block read
        self.serial_port.xonxoff = False  # disable software flow control
        self.serial_port.rtscts = False  # disable hardware (RTS/CTS) flow control
        self.serial_port.dsrdtr = False  # disable hardware (DSR/DTR) flow control
        self.serial_port.writeTimeout = 3  # timeout for write

    def close_serial_port(self):
        """Closes the serial port attached to the modem."""
        print("Closing Serial Port")
        try:
            if self.serial_port.isOpen():
                self.serial_port.close()
                print("Serial Port closed...")
        except:
            print "Error: Unable to close the Serial Port."
            sys.exit()

    # https://github.com/pyserial/pyserial/issues/216#issuecomment-369414522
    def _readline(self):
        i = self.read_buffer.find(b"\n")
        if i >= 0:
            r = self.read_buffer[:i+1]
            self.read_buffer = self.read_buffer[i+1:]
            return r
        while True:
            i = max(1, min(2048, self.serial_port.in_waiting))
            data = self.serial_port.read(i)  # will block up to timeout value
            i = data.find(b"\n")
            if i >= 0:
                r = self.read_buffer + data[:i+1]
                self.read_buffer[0:] = data[i+1:]
                return r
            else:
                self.read_buffer.extend(data)
