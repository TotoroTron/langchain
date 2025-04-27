#!/bin/bash

source ~/workspace/tools/anaconda3/etc/profile.d/conda.sh
conda activate langchain
rm -rf src/*
rm -rf test/*
python main.py >stdout.txt 2>stderr.txt
