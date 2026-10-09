import _socket
from django.apps import AppConfig

# Ensure IPv4 resolution for Google SMTP to prevent Windows / JioFiber IPv6 routing timeout
orig_gai = _socket.getaddrinfo


def _ipv4_forced_gai(host, port, family=0, type=0, proto=0, flags=0):
    if host in ('smtp.gmail.com', 'gmail.com'):
        family = _socket.AF_INET
    return orig_gai(host, port, family, type, proto, flags)


_socket.getaddrinfo = _ipv4_forced_gai


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = 'Email & Notifications'
