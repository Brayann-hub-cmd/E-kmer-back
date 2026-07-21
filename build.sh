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
    user, created = Users.objects.get_or_create(
        email=email,
        defaults={
            'username': username,
            'telephone': telephone,
            'password': password,
            'role': 'admin',
            'is_active': True
        }
    )
    if created:
        print(f'Admin cree: {email}')
    else:
        print(f'Admin deja existant, aucune modification: {email}')
"