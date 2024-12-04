#!/bin/sh

# run inside virtual environment

ruff check --select I --fix
ruff format
