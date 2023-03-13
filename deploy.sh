#!/bin/bash

scp main.py pi@raspberrypi:~/
scp collect_data.service pi@raspberrypi:~/.config/systemd/user/
ssh pi@raspberrypi "systemctl --user daemon-reload"
# ssh pi@raspberrypi "systemctl --user restart collect_data.service"
