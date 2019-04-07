#!/usr/bin/env python3
import subprocess
from ipaddress import ip_address, ip_network


reserved_ips = (
    ip_network('0.0.0.0/8'),
    ip_network('10.0.0.0/8'),
    ip_network('100.64.0.0/10'),
    ip_network('127.0.0.0/8'),
    ip_network('169.254.0.0/16'),
    ip_network('172.16.0.0/12'),
    ip_network('192.0.0.0/24'),
    ip_network('192.0.2.0/24'),
    ip_network('192.88.99.0/24'),
    ip_network('192.168.0.0/16'),
    ip_network('198.18.0.0/15'),
    ip_network('198.51.100.0/24'),
    ip_network('203.0.113.0/24'),
    ip_network('224.0.0.0/4'),
    ip_network('240.0.0.0/4'),
    ip_network('255.255.255.255/32'),
)


def get_public_static_ips():
    try:
        ips = subprocess.check_output(['hostname', '-I'])\
            .decode('utf-8')\
            .strip()\
            .split()
    except subprocess.CalledProcessError:
        raise RuntimeError('can not call hostname with option -I')
    public_static_ips = []
    for ip in ips:
        ip_addr = ip_address(ip)
        for reserved_ip in reserved_ips:
            if ip_addr in reserved_ip:
                break
        else:  # no break
            public_static_ips.append(ip)
    return public_static_ips


if __name__ == '__main__':
    for ip in get_public_static_ips():
        print(ip)
