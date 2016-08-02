#!/usr/bin/env bash

if [[ -e vars.sh ]]; then
    . vars.sh
fi

./temp.py
