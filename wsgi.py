"""
WSGI config for VidyAI project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.
"""

import os
import sys
from pathlib import Path

# Add the VidyAI directory to the path
current_dir = Path(__file__).resolve().parent
vidyai_dir = current_dir / 'VidyAI'
sys.path.append(str(vidyai_dir))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vidyai.settings')

# Import the application from the VidyAI/vidyai/wsgi.py file
from vidyai.wsgi import application 