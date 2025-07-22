#!/bin/bash
export ENV=development
export $(grep -v '^#' .env.dev | xargs)
uvicorn main:create_app --factory --reload --host 0.0.0.0 --port 8000 