#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python ekmer/manage.py collectstatic --no-input
python ekmer/manage.py migrate