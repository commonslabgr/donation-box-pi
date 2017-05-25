#! /bin/bash

# Location:
# /home/commonslab/donation-box/scripts/set-pico-values.sh
#
# This script sets the values which are written into
# the flash memory of the PiCo UPS and used by the
# firmware to set the preferences.

# Set the "Fail-Safe Shut Down" (FSSD) timeout
# after which the Raspberry Pi starts to shut down:
#
# Factory default is 120 seconds.
# Minimum is 15 seconds.
# We want 15 seconds (Hex: F)
i2cset -y 1 0x6b 0x09 0x0f

# The communcation with the flash memory is slow.
# We need to wait, otherwise the next write will fail.
sleep 1

# Set the Low-Power ReSTArt (LPRSTA)timer, which defines the time
# that the UPS waits between checks if the power cable has been
# re-connected while the Raspberry Pi is in low-power stand-by
# (i.e. in halt / shut down situation):
#
# Factory default is 5 seconds.
# Minimum is 1 seconds.
# We want 5 seconds - to avoid draining the battery during storage.
i2cset -y 1 0x6b 0x0a 0x05

# The communcation with the flash memory is slow.
# We need to wait, otherwise the next write will fail.
sleep 1

# Set the Batter-Test TimeOut (BTTO), which defines the time
# that the UPS waits between checks if the power cable has been
# re-connected while the Raspberry Pi is on battery
# (i.e. before shut down and to recharge):
#
# Factory default is 5 seconds.
# Minimum is 2 seconds.
# We want 5 seconds (Hex: 0x05)
i2cset -y 1 0x6b 0x0b 0x05

# The communcation with the flash memory is slow.
# We need to wait, otherwise the next write will fail.
sleep 1

# Set the buzzer mode to Automatic,
# which means that it buzzes according to firmware settings.
#
# Factory default Automatic (2).
# Always off is 0, buzz constantly is 1.
# We want Automatic (Hex: 2)
i2cset -y 1 0x6b 0x0e 0x02

# The communcation with the flash memory is slow.
# We need to wait, otherwise the next write will fail.
sleep 1

# Set the Power-Disconnect timeout, which starts counting
# after it looses connection to the UPS-daemon during shut down,
# after the timeout the UPS cuts the power to the Raspberry Pi:
#
# Factory default is 32 seconds.
# Minimum is 32 seconds.
# We want about two minutes, i.e. 128 seconds (Hex: 80)
i2cset -y 1 0x6b 0x18 0x80


