#!/usr/bin/env bash

conda install -c conda-forge fastapi
conda install -c conda-forge uvicorn
conda install -c conda-forge sqlmodel
conda install -c anaconda black
conda update --all

cp config.py.dist config.py
nano config.py
