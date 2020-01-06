#!/bin/bash

# if app_db database already exists, drop it
if psql -lqt | cut -d \| -f 1 | grep -qw 'app_db'; then
  dropdb app_db
fi

# create the app_db database and set the owner to the current user
createdb app_db