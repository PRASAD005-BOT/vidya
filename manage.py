#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    # Add VidyAI directory to path
    current_dir = Path(__file__).resolve().parent
    vidyai_dir = current_dir / 'VidyAI'
    sys.path.append(str(vidyai_dir))
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vidyai.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main() 