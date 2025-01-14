#!/bin/bash

# docker config
docker/test_env.sh

# downlaod the dependencies
pip install -r requirements.txt

# populate the database
python manage.py setupdata

# run the server
python manage.py runserver