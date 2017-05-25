#!/bin/bash
if [[ ! "$(ps -aux | grep picofssd)" =~ "picofssd.py" ]]
then
    wall Starting pico
    /usr/bin/python /home/commonslab/donation-box/scripts/picofssd.py
fi
