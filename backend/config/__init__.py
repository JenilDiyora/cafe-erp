import _socket

# Enforce IPv4 DNS resolution for Google SMTP to prevent Windows and JioFiber IPv6 routing timeouts
_orig_gai = _socket.getaddrinfo


def _ipv4_forced_gai(host, port, family=0, type=0, proto=0, flags=0):
    if host in ('smtp.gmail.com', 'gmail.com'):
        family = _socket.AF_INET
    return _orig_gai(host, port, family, type, proto, flags)


_socket.getaddrinfo = _ipv4_forced_gai
