"""
Settings module for MajobaCore project.

This module provides different settings configurations for different environments:
- development: For local development
- production: For production deployment
- testing: For running tests

Usage:
- Set DJANGO_SETTINGS_MODULE environment variable to specify which settings to use
- Default is development settings

Examples:
    export DJANGO_SETTINGS_MODULE=majobacore.settings.production
    export DJANGO_SETTINGS_MODULE=majobacore.settings.development
    export DJANGO_SETTINGS_MODULE=majobacore.settings.testing
"""

import os
import sys

# Default to development settings if not specified
default_settings = 'majobacore.settings.development'

# Check if we're running tests
# Get settings module from environment or use default
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', default_settings)

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
