#!/bin/bash
#DonationBox startup script

#Run Web Socket Server
/usr/bin/python /home/commonslab/donation-box/DonationServer.py &

###BEGIN TOUCH SCREEN
#Get touch screen device id
#id=`xinput -list | grep Edamak | sed -n 's/.*\(id=\)//p' | sed -n 's/\t.*//p'`
#id=`xinput -list | grep ILITEK | sed -n 's/.*\(id=\)//p' | sed -n 's/\t.*//p'`
#Calibrate ASUS ILITEK for portrait mode
#xinput set-prop $id "Evdev Axis Calibration" 43 11072 6131 1
#Calibrate LG Touch screen
#/usr/bin/xinput set-int-prop "Edamak LG TS2009F-USB" "Evdev Axis Calibration" 32 -50 2044 1 2088
#/usr/bin/xinput set-int-prop "Edamak LG TS2009F-USB" "Evdev Axes Swap" 8 0
###END TOUCH screen


#Set screen saver and blank off
/usr/bin/xset s off
/usr/bin/xset -dpms
/usr/bin/xset s noblank

#Start sceensaver
#/usr/bin/xscreensaver -nosplash &
#Run Video Screensaver
#/usr/bin/chromium-browser http://donationbox/Video-Fullscreen.html --kiosk &
#Start Chromium for touch screen
#/usr/bin/chromium-browser http://donationbox/ --kiosk --incognito --touch-devices=$id &
#Wait to make sure mySQL and nGinx are running
sleep 15s
#Start Chromium
/usr/bin/chromium-browser http://donationbox/project-1 --kiosk --incognito &

### BEGIN joystic
#For when joystic runs with USB encoder as a gamepad
#sleep 90s
#/home/commonslab/donation-box/scripts/joystick.sh &
#xdotool click 1
#sleep 2s
#xdotool click 1
### END Joystic

###BEGIN Monitor
#Turn On Monitor
#sudo /home/commonslab/donation-box/scripts/monitorOn.sh
#Run Reaction Game
#/home/commonslab/donation-box/game.sh
#Switch to Crowd funding on top
#wmctrl -a
###END Monitor
