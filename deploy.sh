#!/bin/bash

scp main.py pi@raspberrypi:~/
ssh pi@raspberrypi systemctl --user restart collect_data.service
