#!/bin/sh
#Initialize GPIO for monitor
echo "9" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio9/direction
