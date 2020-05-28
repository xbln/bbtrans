#!/bin/bash
# Script zum Start des BB Transfers
cd /home/pydev/bb
source env0/bin/activate
python l.py
mv app.log app_$(date +%F-%H:%M).log
