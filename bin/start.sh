#!/bin/bash
# Start the Call Attendant service
# See the unit file: /lib/systemd/system/callattendant.service
sudo systemctl start callattendant.service
sudo systemctl status callattendant.service
