#!/bin/bash
LOG_DIR=logs
for f in app.log error.log; do
  if [ -f "$LOG_DIR/$f" ]; then
    mv "$LOG_DIR/$f" "$LOG_DIR/$f.$(date +%Y%m%d%H%M%S)"
    touch "$LOG_DIR/$f"
  fi
done 