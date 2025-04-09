#!/bin/bash

# Path to Vivado tools
export XILINX_VIVADO=/home/bcheng/workspace/tools/Xilinx/Vivado/2023.2
export PATH="$PATH:$XILINX_VIVADO/bin"

PROJ_DIR="/home/bcheng/workspace/dev/langchain/ex4"
SRC_DIR="$PROJ_DIR/hdl/src"
VERIF_DIR="$PROJ_DIR/hdl/verif"

# https://itsembedded.com/dhd/vivado_sim_1/

# parse the files.
xvlog "$SRC_DIR/top_level.v"
xvlog --sv "$VERIF_DIR/top_level_tb.sv"

# elaboration: search and bind instantiated Verilog design units.
xelab -top top_level_tb -snapshot sim_snapshot -timescale 1ns/1ps -debug typical

# xsim_config.tcl
# log_wave -recursive *
# run all
# exit

# launch the simulation
xsim sim_snapshot --tclbatch xsim_config.tcl
