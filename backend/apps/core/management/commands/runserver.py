"""Custom runserver command that defaults to listening on 0.0.0.0:8000.

This enables immediate access from other devices on the local network (such as mobile phones)
without needing to manually specify 0.0.0.0:8000 every time.
"""

from django.contrib.staticfiles.management.commands.runserver import Command as StaticfilesRunserverCommand


class Command(StaticfilesRunserverCommand):
    default_addr = '0.0.0.0'
    default_port = '8000'

