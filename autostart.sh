!#/bin/bash

# This file only exists to nake it dead simple to deactivate the autostart of the script,
# instead of having to edit the /etc/xdg/autostart/buzzer.desktop file, which calls this.

DO_AUTOSTART="true"

if [ $DO_AUTOSTART = "true" ]
then
    rm autostart_log.txt
    python3 buzzer.py > autostart_log.txt
fi
