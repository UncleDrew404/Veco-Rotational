#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


DEFAULT_RUNSERVER_PORT = '8080'


def use_project_runserver_port(argv):
    """Use port 8080 when runserver is called without an address or port."""
    if len(argv) < 2 or argv[1] != 'runserver':
        return

    runserver_arguments = argv[2:]
    if not runserver_arguments or all(
        argument.startswith('-') for argument in runserver_arguments
    ):
        argv.insert(2, DEFAULT_RUNSERVER_PORT)


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    use_project_runserver_port(sys.argv)
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
