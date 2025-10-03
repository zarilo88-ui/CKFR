#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Create/update a superuser without needing shell access
python << 'PY'
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ckfr_site.settings")
django.setup()
from django.contrib.auth import get_user_model

username = os.environ.get("ADMIN_USER", "admin")
email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
password = os.environ.get("ADMIN_PASSWORD")

User = get_user_model()
u, created = User.objects.get_or_create(username=username, defaults={"email": email})
changed = False
if not u.is_superuser:
    u.is_superuser = True
    changed = True
if not u.is_staff:
    u.is_staff = True
    changed = True
if password:
    u.set_password(password); changed = True
if changed:
    if email and u.email != email:
        u.email = email
    u.save()
print(f"Superuser ready: {u.username} (created={created})")
PY