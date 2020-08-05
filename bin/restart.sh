#!/bin/bash
# Start the Call Attendant service

sudo systemctl restart callattendant.service
sudo systemctl status callattendant.service
