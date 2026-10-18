#!/bin/bash

set -e

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-seed"
printf "${CYAN}==== ${LABEL}${NO_COLOR}\n"

# Get the backend directory
backend_dir="$(dirname "$(dirname "$(realpath "$0")")")"

# Run the seed script
python3 "$backend_dir/seed/seed_data.py"

printf "${CYAN}==== ${LABEL} complete${NO_COLOR}\n"
