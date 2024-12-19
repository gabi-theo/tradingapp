#!/bin/bash

REPO_URL="https://github.com/gabi-theo/tradingapp"

DEST_FOLDER="nch"

git clone "$REPO_URL" "$DEST_FOLDER"

if [ $? -eq 0 ]; then
    echo "Repository cloned successfully into '$DEST_FOLDER'."

    echo "DEBUG=False
SECRET_KEY='django-insecure-p_)32csof!z47by56#h@9lznxt7yu4&o+ah%to9lus2+14m@e2'
DATABASE_NAME=nch
DATABASE_USER=postgres
DATABASE_PASSWORD=pgadmin
DATABASE_HOST=postgres
DATABASE_PORT=5432
DEVICE_DATA_TABLE=api_hyetinput" > "$DEST_FOLDER/.env"
    
    echo ".env file generated successfully."
else
    echo "Error: Unable to clone repository."
fi