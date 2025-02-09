#!/bin/bash

pip install mpremote
mpremote cp src/*.py :
mpremote cp config/keys :
mpremote cp config/uprn :
mpremote cp config/wifi :

mpremote run src/install.py
