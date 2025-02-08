#!/bin/bash

# Install system dependencies
yum install -y libjpeg-turbo-devel zlib-devel libtiff-devel freetype-devel lcms2-devel \
    libwebp-devel tcl-devel tk-devel harfbuzz-devel fribidi-devel libraqm-devel libimagequant-devel

# Create symbolic links for libjpeg
ln -s /usr/lib64/libjpeg.so.62 /var/task/libjpeg.so.62

# Install Python dependencies
pip install -r requirements.txt
