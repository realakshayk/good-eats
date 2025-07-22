#!/bin/bash
export ENV=production
export $(grep -v '^#' .env.prod | xargs)
uvicorn main:create_app --factory --host 0.0.0.0 --port 8000 