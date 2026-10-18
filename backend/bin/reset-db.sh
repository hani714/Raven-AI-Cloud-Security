#!/bin/bash

set -e

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-reset"
printf "${CYAN}==== ${LABEL}${NO_COLOR}\n"

bin_path="$(realpath .)/bin"

source "$bin_path/db-pg-drop.sh"
source "$bin_path/db-drop.sh"
source "$bin_path/db-create.sh"
# source "$bin_path/db-migrate.sh"