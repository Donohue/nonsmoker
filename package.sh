#!/bin/sh
mkdir ./tmp
cp -r venv/lib/python3.8/site-packages/* ./tmp/
cp ./src/index.py ./tmp
cd ./tmp
zip -r ../src.zip *
cd ../
rm -rf ./tmp
