#!/bin/bash
python3 -m pip install virtualenv
python3 -m venv tr_venv
source tr_venv/bin/activate
pip3 install -r requirements.txt