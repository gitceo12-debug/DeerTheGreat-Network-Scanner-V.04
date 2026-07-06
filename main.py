#!/usr/bin/env python3
"""
DeerTheGreat - a faster, friendlier, futuristic-looking network port scanner.

Usage examples:
    python3 main.py 192.168.1.1
    python3 main.py 192.168.1.0/24 -p top100
    python3 main.py example.com -p 22,80,443 -c 200 -t 1.5
    python3 main.py 10.0.0.1-50 -p 1-1000 -o results.json

Stdlib only. No installation required beyond Python 3.9+.
"""

import argparse
import asyncio
import json
import sys
import time

import ui
from scanner import ScanConfig, scan_targets_parallel_hosts
from utils import parse_targets, parse_ports, ParseError


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="deerthegreat",
        description="DeerTheGreat - network reconnaissance, reimagined.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("target", help="IP, hostname, CIDR (192.168.1.0/24), or range (192.168.1.1-50). Comma-separated list allowed.")
    p.add_argument("-p", "--ports", default="top100",
                    help="Ports to scan: single(80), list(22,80,443), range(1-1000), 'top100', or 'all'. Default: top100")
    p.add_argument("-c", "--concurrency", type=int, default=500,
                    help="Max simultaneous connection attempts. Default: 500")
    p.add_argument("-t", "--timeout", type=float, default=1.0,
                    help="Per-connection timeout in seconds. Default: 1.0")
    p.add_argument("--no-banner-grab", action="store_true",
                    help="Skip passive banner grabbing (faster).")
    p.add_argument("-o", "--output", default=None,
                    help="Write results to a JSON file at this path.")
    p.add_argument("--no-ui", action="store_true",
                    help="Disable colors/banner/live progress (plain output, good for piping/logging).")
    return p


def render_plain_result(host, port_results):
    open_ports = [r for r in port_results if r.open]
    print(f"\n{host}")
    if not open_ports:
        print("  no open ports found")
    for r in open_ports:
        print(f"  {r.port:<6} {r.service:<15} {r.banner}")


async def run(args) -> int:
    try:
        hosts = parse_targets(args.target)
        ports = parse_ports(args.ports)
    except ParseError as e:
        ui.error(str(e))
        return 1

    if not hosts:
        ui.error("No valid targets to scan.")
        return 1
    if not ports:
        ui.error("No valid ports to scan.")
        return 1

    config = ScanConfig(
        timeout=args.timeout,
        concurrency=args.concurrency,
        grab_banners=not args.no_banner_grab,
    )

    total_checks = len(hosts) * len(ports)

    if not args.no_ui:
        ui.print_banner()
        ui.print_scan_header(len(hosts), len(ports), args.concurrency, args.timeout)
        progress = ui.LiveProgress(total_checks, label="Scanning")

        def on_progress(result):
            progress.update(done_delta=1, open_delta=1 if result.open else 0)
    else:
        print(f"[deerthegreat] scanning {len(hosts)} host(s) x {len(ports)} port(s) = {total_checks} checks")
        progress = None

        def on_progress(result):
            pass

    start = time.time()
    results = await scan_targets_parallel_hosts(hosts, ports, config, on_progress=on_progress)
    elapsed = time.time() - start

    if progress:
        progress.finish()

    output_data = {}
    for host in hosts:
        port_results = results.get(host, [])
        open_ports = [r for r in port_results if r.open]

        if not args.no_ui:
            ui.print_host_result(
                host,
                [{"port": r.port, "service": r.service, "banner": r.banner} for r in open_ports],
            )
        else:
            render_plain_result(host, port_results)

        output_data[host] = [
            {"port": r.port, "service": r.service, "banner": r.banner} for r in open_ports
        ]

    if not args.no_ui:
        ui.print_summary(output_data, elapsed)
    else:
        total_open = sum(len(v) for v in output_data.values())
        print(f"\n[deerthegreat] done. {total_open} open port(s) across {len(hosts)} host(s) in {elapsed:.2f}s")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        if not args.no_ui:
            ui.info(f"Results written to {args.output}")
        else:
            print(f"[deerthegreat] results written to {args.output}")

    return 0


def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    try:
        return asyncio.run(run(args))
    except KeyboardInterrupt:
        print("\n\ninterrupted, exiting.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
