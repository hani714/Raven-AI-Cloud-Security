#!/bin/bash

# Colors
CYAN='\033[1;36m'
GREEN='\033[1;32m'
RED='\033[1;31m'
NO_COLOR='\033[0m'
LABEL="db-migrate"

printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

# Step 1: Check if virtual environment is active
if [[ -z "$VIRTUAL_ENV" ]]; then
  printf "${RED}Error:${NO_COLOR} Virtual environment not activated.\n"
  printf "Run: ${GREEN}source venv/bin/activate${NO_COLOR}\n"
  exit 1
fi

# Step 2: Run Alembic migrations
printf "${CYAN}Running Alembic upgrade...${NO_COLOR}\n"
alembic upgrade head

# Step 3: Status message
if [ $? -eq 0 ]; then
  printf "${GREEN}Migration successful!${NO_COLOR}\n"
else
  printf "${RED}Migration failed.${NO_COLOR}\n"
fi
