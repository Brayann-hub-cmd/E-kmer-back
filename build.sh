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
python ekmer/manage.py shell -c "
from api.models import Users, Livreur

livreurs = '$LIVREUR_ACCOUNTS'.split(';')
for livreur in livreurs:
    parts = livreur.split(',')
    if len(parts) != 7:
        continue
    username, email, password, telephone, type_vehicule, num_permis, num_plaque = parts
    user, created = Users.objects.get_or_create(
        email=email,
        defaults={
            'username': username,
            'telephone': telephone,
            'password': password,
            'role': 'livreur',
            'is_active': True
        }
    )
    if created:
        print(f'Livreur cree: {email}')
    else:
        print(f'Livreur deja existant: {email}')

    Livreur.objects.get_or_create(
        user=user,
        defaults={
            'type_vehicule': type_vehicule,
            'num_permis': num_permis,
            'num_plaque': num_plaque,
            'disponible': True,
            'is_validated': True
        }
    )
"