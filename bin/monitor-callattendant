#!/bin/bash
# Show the callattendent service log. Start the log 35 lines back
# so we can see the call attendant's configuration dump.

sudo journalctl --follow -n 35 --no-hostname -u callattendant.service
