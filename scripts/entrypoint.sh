#!/bin/sh

python ./src/main.py main-preprocess-comments && \
python ./src/main.py main-preprocess-images &&  \
python ./src/main.py main-extract-text-images
