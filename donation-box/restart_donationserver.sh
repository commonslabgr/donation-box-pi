#!/bin/bash
echo 'Terminating DonationServer.py'
pkill -f "DonationServer.py"
echo 'Starting DonationServer.py'
./DonationServer.py &
