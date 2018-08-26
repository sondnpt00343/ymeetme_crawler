#!/bin/bash
echo "stop bot"
pkill -9 "Web Content"
pkill -9 "firefox-esr"
pkill -9 "Xvfb"
pkill -9 "geckodriver"
pkill -9 python
echo "stop bot completed"

