#!/bin/bash

if [ ! -f "db/cinemabot.db" ]; then
    python backend/db.py
fi

exec python backend/server.py
