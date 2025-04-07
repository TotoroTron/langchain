#!/bin/bash

source ~/workspace/tools/anaconda3/etc/profile.d/conda.sh
conda activate langchain
python3 main.py &>output.txt
