#!/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-drop"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

cd "$(dirname "$0")/.."

MONGO_URI="mongodb://localhost:27017"
MONGO_DB="awspentest"

echo "Using mongosh to drop database ${MONGO_DB} at ${MONGO_URI}"
if mongosh "${MONGO_URI}/${MONGO_DB}" --eval "printjson(db.getName())" >/dev/null 2>&1; then
    echo "Dropping MongoDB database: ${MONGO_DB}"
    mongosh "${MONGO_URI}/${MONGO_DB}" --eval "db.dropDatabase(); print('Dropped: ${MONGO_DB}')"
else
    echo "→ Database '${MONGO_DB}' does not exist or connection failed — skipping drop."
fi

printf "${CYAN}== ${LABEL} completed${NO_COLOR}\n"