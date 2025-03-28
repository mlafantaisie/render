#!/usr/bin/env python
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  # ✅ Ensure settings are loaded

    try:
        from django.core.management import execute_from_command_line
        import django
        django.setup()  # ✅ Initialize Django explicitly (important for migrations)
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable?"
        ) from exc

    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
