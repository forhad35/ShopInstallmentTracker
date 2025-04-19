#!/bin/bash

# Start the FastAPI app
uvicorn app.main:app --host=0.0.0.0 --port=10000
