#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python ekmer/manage.py collectstatic --no-input
python ekmer/manage.py migrate
python ekmer/manage.py shell -c "
from api.models import Users

admins = '$ADMIN_ACCOUNTS'.split(';')
for admin in admins:
    parts = admin.split(',')
    if len(parts) != 4:
        continue
    username, email, password, telephone = parts
    Users.objects.filter(email=email).delete()
    Users.objects.create(
        username=username,
        email=email,
        telephone=telephone,
        password=password,
        role='admin',
        is_active=True
    )
    print(f'Admin recree: {email}')
"