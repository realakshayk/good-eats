#!/bin/bash
if [ -f pyproject.toml ]; then
  pip install poetry && poetry install
else
  pip install -r requirements.txt
fi 