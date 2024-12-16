#!/bin/bash

# Start the backend
(cd backend && poetry run python3 src/game/app.py) &

# Start the frontend
(cd frontend && ng serve --poll=2000)