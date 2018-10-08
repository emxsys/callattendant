#!/usr/bin/python
# -*- coding: UTF-8 -*-

from datetime import datetime
import serial
import subprocess
import threading


class Modem(object):
    def __init__(self):
        self.serial_port = serial.Serial()
        # Event processing is disabled until we send our first command
        self.disable_event_processing = True
        self.init_modem()

        self.event_thread = threading.Thread(target=self.process_events)
        self.event_thread.start()


    def init_modem(self):

        # Detect and Open the Modem Serial COM Port
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
            if not self.exec_cmd("AT"):
                print "Error: Unable to access the Modem"

            # reset to factory default.
            if not self.exec_cmd("ATZ3"):
                print "Error: Unable reset to factory default"

                # Display result codes in verbose form
            if not self.send_cmd("ATV1"):
                print "Error: Unable set response in verbose form"

                # Enable Command Echo Mode.
            if not self.send_cmd("ATE1"):
                print "Error: Failed to enable Command Echo Mode"

                # Enable formatted caller report.
            if not self.send_cmd("AT+VCID=1"):
                print "Error: Failed to enable formatted caller report."

            # Flush any existing input outout data from the buffers
            self.serial_port.flushInput()
            self.serial_port.flushOutput()

        except:
            print "Error: unable to Initialize the Modem"
            sys.exit()

    def open_serial_port(self):
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
                    # Try to put Modem in Voice Mode
                    if not self.send_cmd("AT+FCLASS=8", "OK"):
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
        # Close the Serial COM Port
        try:
            if self.serial_port.isOpen():
                self.serial_port.close()
                print ("Serial Port closed...")
        except:
            print "Error: Unable to close the Serial Port."
            sys.exit()


    def process_events(self):
        # Call detail dictionary
        call_record = {}

        while 1:
            if not self.disable_event_processing:
                modem_data = self.serial_port.readline()

                if modem_data != "":
                    print modem_data

                    if ("DATE" in modem_data):
                        call_record['DATE'] = (modem_data[5:]).strip(' \t\n\r')
                    if ("TIME" in modem_data):
                        call_record['TIME'] = (modem_data[5:]).strip(' \t\n\r')
                    if ("NMBR" in modem_data):
                        call_record['NMBR'] = (modem_data[5:]).strip(' \t\n\r')
                        # Call call details logger
                        print call_record
                        # call_details_logger(call_record)

                    if "RING" in modem_data.strip(chr(16)):
                        pass


    def send_cmd(self, command, expected_response="OK"):
        # Disable processing input while sending commands
        self.disable_event_processing = True

        try:
            # Send command to the Modem
            self.serial_port.write((command + "\r").encode())
            # Read Modem response
            execution_status = self.read_cmd_response(expected_response)
            self.disable_event_processing = False
            # Return command execution status
            return execution_status

        except:
            self.disable_event_processing = False
            print "Error: Failed to execute the command"
            return False


    def read_cmd_response(self, expected_response="OK"):
        # Set the auto timeout interval
        start_time = datetime.now()

        MODEM_RESPONSE_READ_TIMEOUT = 10  # Tine in Seconds

        try:
            while 1:
                # Read Modem Data on Serial Rx Pin
                modem_response = self.serial_port.readline()
                print modem_response
                # Recieved expected Response
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
