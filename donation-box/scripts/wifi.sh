#!/bin/sh

nmcli radio wifi off
rfkill unblock wlan
service isc-dhcp-server restart
hostapd -d /etc/hostapd/hostapd.conf &

