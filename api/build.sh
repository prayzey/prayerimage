#!/bin/bash

# First install Pillow without dependencies
pip install Pillow==8.4.0 --no-deps

# Then install everything else
pip install -r requirements.txt
