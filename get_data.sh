#!/bin/bash

mkdir -p data
scp -r pi@raspberrypi:~/data/*.csv data
