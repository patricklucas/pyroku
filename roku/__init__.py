import os
import socket
import urlparse
import time

ROKU_HOST_DOTFILE = os.path.expanduser("~/.roku")
ROKU_HOST_DOTFILE_TTL = 3600

SSDP_MULTICAST = ("239.255.255.250", 1900)


def discover_roku():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    req = '\r\n'.join([
        "M-SEARCH * HTTP/1.1",
        "HOST: %s:%d" % SSDP_MULTICAST,
        "Man: \"ssdp:discover\"",
        "ST: roku:ecp",
        ""
    ])

    sock.sendto(req, SSDP_MULTICAST)
    resp, _ = sock.recvfrom(1024)

    for line in resp.splitlines():
        if not line.startswith('Location: '):
            continue

        url = line[10:]
        _, netloc, _, _, _, _ = urlparse.urlparse(url)

        return netloc


def get_roku_host():
    if os.path.isfile(ROKU_HOST_DOTFILE):
        mtime = os.stat(ROKU_HOST_DOTFILE).st_mtime
        if time.time() - mtime < ROKU_HOST_DOTFILE_TTL:
            with open(ROKU_HOST_DOTFILE) as f:
                return f.read().strip()

    roku_host = discover_roku()

    with open(ROKU_HOST_DOTFILE, 'w') as f:
        f.write(roku_host + '\n')

    return roku_host
