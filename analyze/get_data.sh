#!/bin/bash

mkdir -p data
scp -r fridge:/opt/fridge/data/*.csv data
