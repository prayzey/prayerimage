#!/bin/bash

# Create lib directory in the build output
mkdir -p .vercel/output/lib

# Copy system libraries
cp /usr/lib64/libjpeg.so.62* .vercel/output/lib/
cp /usr/lib64/libpng16.so.16* .vercel/output/lib/
cp /usr/lib64/libz.so.1* .vercel/output/lib/
cp /usr/lib64/libtiff.so.5* .vercel/output/lib/

# Set LD_LIBRARY_PATH in the runtime
echo 'export LD_LIBRARY_PATH=/var/task/lib:$LD_LIBRARY_PATH' > .vercel/output/config.sh

# Install Python dependencies
pip install --target .vercel/output/python -r requirements.txt

# Copy application files
cp -r api .vercel/output/
cp prayer_image.py .vercel/output/

# Create the Vercel output configuration
cat > .vercel/output/config.json << EOF
{
  "version": 3,
  "routes": [
    { "src": "/(.*)", "dest": "/api/index.py" }
  ],
  "env": {
    "LD_LIBRARY_PATH": "/var/task/lib"
  }
}
EOF
