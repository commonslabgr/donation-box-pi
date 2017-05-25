#!/bin/bash

while true; do
  mode=$(i2cget -y 1 0x69 0x00 b)
  echo "Mode: $mode"  
  sleep 1
  counter=0
  while [ "$mode" == "0x02" ]; do
    counter=$[counter+1]
    mode=$(i2cget -y 1 0x69 0x00 b)
    sleep 1
    echo "Counter: $counter"
    if [ "$mode" == "0x01" ]; then
      break
    fi  
    if [ $counter -eq 10 ]; then
      shutdown -h now
      break
    fi
  done
done
