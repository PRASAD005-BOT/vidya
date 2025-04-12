"""
WSGI config for vidyai project.

It exposes the WSGI callable as a module-level variable named `application`.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

# Add the parent directory to the sys.path
current_path = os.path.dirname(os.path.abspath(_file_))
parent_path = os.path.dirname(current_path)
sys.path.append(parent_path)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vidyai.settings')

application = get_wsgi_application()
