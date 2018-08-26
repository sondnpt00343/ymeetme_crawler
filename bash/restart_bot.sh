#!/bin/bash
echo "start bot $1"
pkill -9 "Web Content"
pkill -9 "firefox-esr"
pkill -9 "Xvfb"
pkill -9 "geckodriver"
pkill -9 python
cd /usr/src/mybot-bnb
commandline=$(nohup python start.py -i $1 >> /usr/src/mybot-bnb/logs/$1.log)&
echo "start bot $1 completed"

