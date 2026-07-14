#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python ekmer/manage.py collectstatic --no-input
python ekmer/manage.py migrate

python ekmer/manage.py shell -c "
import bcrypt
from api.models import Users

admins = '$ADMIN_ACCOUNTS'.split(';')
for admin in admins:
    parts = admin.split(',')
    if len(parts) != 4:
        continue
    username, email, password, telephone = parts
    if not Users.objects.filter(email=email).exists():
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        Users.objects.create(
            username=username,
            email=email,
            telephone=telephone,
            password=hashed,
            role='admin',
            is_active=True
        )
        print(f'Admin cree: {email}')
    else:
        print(f'Admin existe deja: {email}')
"
"