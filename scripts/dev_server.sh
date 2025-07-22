#!/bin/bash
export ENV=development
uvicorn main:create_app --factory --reload --host 0.0.0.0 --port 8000 