#!/bin/bash
# Stop the Call Attendant service

sudo systemctl stop callattendant.service
sudo systemctl status callattendant.service
