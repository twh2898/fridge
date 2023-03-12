#!/bin/bash

mkdir -p data
scp -r pi@raspberrypi:~/data/* data
