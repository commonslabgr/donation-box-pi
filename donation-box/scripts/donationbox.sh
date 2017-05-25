#!/bin/bash
#DonationBox startup script

echo "Script running" >> donationbox.txt

#Run PIco UPS listener
#it is in rc.local
#sudo /home/commonslab/donation-box/scripts/picocounter.sh &
#Run Serial deamon for listening to Coin Acceptor
#it is in rc.local
#sudo /usr/bin/python /home/commonslab/donation-box/Serial2DB.py &
#Run Web Socket Server
/usr/bin/python /home/commonslab/donation-box/DonationServer.py &
#/usr/bin/python /home/commonslab/donation-box/wsServer.py &

#Get touch screen device id
#id=`xinput -list | grep Edamak | sed -n 's/.*\(id=\)//p' | sed -n 's/\t.*//p'`
#id=`xinput -list | grep ILITEK | sed -n 's/.*\(id=\)//p' | sed -n 's/\t.*//p'`

#Calibrate ASUS ILITEK for portrait mode
#xinput set-prop $id "Evdev Axis Calibration" 43 11072 6131 1

#Set screen saver and blank off
/usr/bin/xset s off
/usr/bin/xset -dpms
/usr/bin/xset s noblank
#Calibrate LG Touch screen
#/usr/bin/xinput set-int-prop "Edamak LG TS2009F-USB" "Evdev Axis Calibration" 32 -50 2044 1 2088
#/usr/bin/xinput set-int-prop "Edamak LG TS2009F-USB" "Evdev Axes Swap" 8 0
#Start sceensaver
#/usr/bin/xscreensaver -nosplash &
#Run Video Screensaver
#/usr/bin/chromium-browser http://donationbox/Video-Fullscreen.html --kiosk &
#Start Chromium
#/usr/bin/chromium-browser http://donationbox/ --kiosk --incognito --touch-devices=$id &
sleep 10s
/usr/bin/chromium-browser http://donationbox/project-1 --kiosk --incognito &
sleep 90s
/home/commonslab/donation-box/scripts/joystick.sh &
xdotool click 1
sleep 2s
xdotool click 1
#Turn On Monitor
#sudo /home/commonslab/donation-box/scripts/monitorOn.sh
#Run Reaction Game
#/home/commonslab/donation-box/game.sh
#Switch to Crowd funding on top
#wmctrl -a
