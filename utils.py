"""
utils.py - Target parsing, port parsing, and known-service lookup for DeerTheGreat.
Pure standard library. No external dependencies.
"""

import ipaddress
import socket

COMMON_SERVICES = {
    20: "ftp-data", 21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
    53: "dns", 67: "dhcp", 68: "dhcp", 69: "tftp", 80: "http",
    110: "pop3", 111: "rpcbind", 119: "nntp", 123: "ntp", 135: "msrpc",
    137: "netbios-ns", 138: "netbios-dgm", 139: "netbios-ssn", 143: "imap",
    161: "snmp", 162: "snmptrap", 179: "bgp", 194: "irc", 389: "ldap",
    443: "https", 445: "microsoft-ds", 465: "smtps", 514: "syslog",
    515: "printer", 587: "submission", 631: "ipp", 636: "ldaps",
    993: "imaps", 995: "pop3s", 1080: "socks", 1433: "mssql",
    1521: "oracle", 1723: "pptp", 2049: "nfs", 2375: "docker",
    3000: "dev-http", 3128: "squid-proxy", 3306: "mysql", 3389: "rdp",
    5000: "upnp/dev-http", 5432: "postgresql", 5601: "kibana",
    5900: "vnc", 5985: "winrm-http", 5986: "winrm-https", 6379: "redis",
    6443: "kubernetes-api", 7001: "weblogic", 8000: "http-alt",
    8008: "http-alt", 8080: "http-proxy", 8081: "http-alt",
    8443: "https-alt", 8888: "http-alt", 9000: "sonarqube/php-fpm",
    9200: "elasticsearch", 9300: "elasticsearch-node", 11211: "memcached",
    27017: "mongodb", 27018: "mongodb", 50000: "sap",
}

TOP_100_PORTS = sorted(set(list(COMMON_SERVICES.keys()) + [
    1, 7, 9, 13, 17, 19, 26, 37, 49, 70, 79, 81, 88, 90, 106, 113, 199,
    256, 264, 280, 311, 406, 407, 416, 417, 425, 427, 444, 458, 464,
    500, 512, 513, 543, 544, 548, 554, 556, 563, 587, 593, 616, 617,
    625, 646, 648, 666, 691, 706, 771, 777, 783, 787, 800, 801, 808,
    843, 873, 902, 903, 981, 990, 992, 995, 999, 1000, 1001, 1010,
    1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035,
    1036, 1037, 1038, 1039, 1040, 1041, 1044, 1050, 1067, 1068, 1076,
    1080, 1083, 1084, 1099, 1100, 1109, 1110, 1112, 1113, 1114, 1117,
    1119, 1121, 1122, 1131, 1138, 1141, 1145, 1147, 1148, 1149, 1151,
    1152, 1154, 1163, 1164, 1165, 1166, 1169, 1174, 1175, 1183, 1185,
    1186, 1187, 1192, 1198, 1199, 1201, 1213, 1216, 1217, 1218, 1233,
    1234, 1236, 1244, 1247, 1248, 1259, 1271, 1272, 1277, 1287, 1296,
    1300, 1301, 1309, 1310, 1311, 1322, 1328, 1334, 1352, 1417, 1433,
    1434, 1443, 1455, 1461, 1494, 1500, 1501, 1503, 1521, 1524, 1533,
    1556, 1580, 1583, 1594, 1600, 1641, 1658, 1666, 1687, 1688, 1700,
]))[:100]


class ParseError(Exception):
    pass


def resolve_host(target: str) -> str:
    """Resolve a hostname to an IP address (or return the IP if already one)."""
    try:
        ipaddress.ip_address(target)
        return target
    except ValueError:
        try:
            return socket.gethostbyname(target)
        except socket.gaierror as e:
            raise ParseError(f"Could not resolve host '{target}': {e}")


def parse_targets(spec: str) -> list[str]:
    """
    Parse a target specification into a list of IP address strings.
    Supports:
      - single IP:            192.168.1.1
      - hostname:             example.com
      - CIDR notation:        192.168.1.0/24
      - dash range (last octet): 192.168.1.1-50
      - comma-separated list of any of the above
    """
    targets: list[str] = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue

        if "/" in chunk:
            try:
                net = ipaddress.ip_network(chunk, strict=False)
                targets.extend(str(ip) for ip in net.hosts())
            except ValueError as e:
                raise ParseError(f"Invalid CIDR '{chunk}': {e}")

        elif "-" in chunk and chunk.count(".") == 3:
            base, _, end = chunk.rpartition("-")
            try:
                prefix = ".".join(base.split(".")[:3])
                start_octet = int(base.split(".")[3])
                end_octet = int(end)
                if not (0 <= start_octet <= 255 and 0 <= end_octet <= 255):
                    raise ValueError("octet out of range")
                for o in range(start_octet, end_octet + 1):
                    targets.append(f"{prefix}.{o}")
            except (ValueError, IndexError) as e:
                raise ParseError(f"Invalid range '{chunk}': {e}")

        else:
            targets.append(resolve_host(chunk))

    seen = set()
    unique = []
    for t in targets:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique


def parse_ports(spec: str) -> list[int]:
    """
    Parse a port specification into a sorted list of unique ints.
    Supports:
      - single port:       80
      - list:              22,80,443
      - range:             1-1000
      - mixed:             22,80,1000-2000
      - keyword 'top100':  top 100 common ports
      - keyword 'all':     1-65535
    """
    spec = spec.strip().lower()
    if spec in ("top100", "top", "common"):
        return TOP_100_PORTS
    if spec == "all":
        return list(range(1, 65536))

    ports: set[int] = set()
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            try:
                lo, hi = chunk.split("-")
                lo, hi = int(lo), int(hi)
            except ValueError:
                raise ParseError(f"Invalid port range '{chunk}'")
            if not (1 <= lo <= 65535 and 1 <= hi <= 65535 and lo <= hi):
                raise ParseError(f"Port range out of bounds: '{chunk}'")
            ports.update(range(lo, hi + 1))
        else:
            try:
                p = int(chunk)
            except ValueError:
                raise ParseError(f"Invalid port '{chunk}'")
            if not (1 <= p <= 65535):
                raise ParseError(f"Port out of range: {p}")
            ports.add(p)
    return sorted(ports)


def service_name(port: int) -> str:
    return COMMON_SERVICES.get(port, "unknown")
