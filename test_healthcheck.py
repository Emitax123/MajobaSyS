#!/usr/bin/env python
"""
Script simple para probar el endpoint de healthcheck.
"""
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'majobacore.settings.production')
os.environ.setdefault('SECRET_KEY', 'test-key-for-healthcheck')
os.environ.setdefault('ALLOWED_HOSTS', 'localhost')

import django
django.setup()

from django.test import RequestFactory
from majobacore.views import liveness_check

# Crear request factory
rf = RequestFactory()

# Probar liveness check
print("Testing /health/live/ endpoint...")
req = rf.get('/health/live/')
response = liveness_check(req)

print(f"✓ Status Code: {response.status_code}")
print(f"✓ Content: {response.content.decode()}")
print(f"✓ Content-Type: {response.get('Content-Type', 'not set')}")

if response.status_code == 200:
    print("\n✅ SUCCESS: Healthcheck endpoint is working correctly!")
    print("Railway will be able to verify your application is running.")
    sys.exit(0)
else:
    print(f"\n❌ FAILED: Expected 200, got {response.status_code}")
    sys.exit(1)
