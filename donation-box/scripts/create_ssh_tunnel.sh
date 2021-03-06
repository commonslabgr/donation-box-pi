#!/bin/bash
createTunnel() {
  /usr/bin/ssh -N -R 2222:localhost:2222 donationbox@commonslab.gr
  if [[ $? -eq 0 ]]; then
    echo Tunnel to jumpbox created successfully
  else
    echo An error occurred creating a tunnel to jumpbox. RC was $?
  fi
}
/bin/pidof ssh
if [[ $? -ne 0 ]]; then
  echo Creating new tunnel connection
  createTunnel
fi

