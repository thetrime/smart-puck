#!/bin/bash

pip install mpremote
mpremote cp *.py :
mpremote cp keys :
mpremote cp uprn :
mpremote cp wifi :

mpremote run install.py
