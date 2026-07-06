"""
scanner.py - Core async scanning engine for DeerTheGreat.
Pure standard library (asyncio + socket). No raw sockets, no root required.

Performs TCP connect scanning: for each (host, port) pair it attempts a full
TCP handshake. This is the same fundamentally legal, standard technique
`nmap -sT` uses — it just tries to connect, like any client application does.
"""

import asyncio
import socket
from dataclasses import dataclass, field

from utils import service_name


@dataclass
class PortResult:
    port: int
    open: bool
    service: str
    banner: str = ""


@dataclass
class ScanConfig:
    timeout: float = 1.0
    concurrency: int = 500
    grab_banners: bool = True
    banner_timeout: float = 0.6


async def _grab_banner(reader: asyncio.StreamReader, timeout: float) -> str:
    """Try to passively read a service banner (e.g. SSH version string, HTTP header)."""
    try:
        data = await asyncio.wait_for(reader.read(256), timeout=timeout)
        if data:
            return data.decode(errors="replace").strip().replace("\r", " ").replace("\n", " ")
    except (asyncio.TimeoutError, ConnectionError, OSError):
        pass
    return ""


async def scan_port(host: str, port: int, config: ScanConfig, sem: asyncio.Semaphore) -> PortResult:
    async with sem:
        try:
            fut = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(fut, timeout=config.timeout)
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError, socket.gaierror):
            return PortResult(port=port, open=False, service=service_name(port))

        banner = ""
        if config.grab_banners:
            banner = await _grab_banner(reader, config.banner_timeout)

        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

        return PortResult(port=port, open=True, service=service_name(port), banner=banner)


async def scan_host(
    host: str,
    ports: list[int],
    config: ScanConfig,
    sem: asyncio.Semaphore,
    on_progress=None,
) -> list[PortResult]:
    """Scan all requested ports on a single host, reporting progress as each finishes."""
    results: list[PortResult] = []

    async def _wrapped(p):
        res = await scan_port(host, p, config, sem)
        if on_progress:
            on_progress(res)
        return res

    tasks = [asyncio.create_task(_wrapped(p)) for p in ports]
    for coro in asyncio.as_completed(tasks):
        results.append(await coro)

    results.sort(key=lambda r: r.port)
    return results


async def scan_targets(
    hosts: list[str],
    ports: list[int],
    config: ScanConfig,
    on_progress=None,
) -> dict[str, list[PortResult]]:
    """
    Scan multiple hosts. Concurrency is shared across the whole run via a single
    semaphore so --concurrency behaves predictably regardless of host count.
    """
    sem = asyncio.Semaphore(config.concurrency)
    results: dict[str, list[PortResult]] = {}
    for host in hosts:
        results[host] = await scan_host(host, ports, config, sem, on_progress=on_progress)
    return results


async def scan_targets_parallel_hosts(
    hosts: list[str],
    ports: list[int],
    config: ScanConfig,
    on_progress=None,
) -> dict[str, list[PortResult]]:
    """
    Alternative scheduling: scan all hosts concurrently too (not just ports within
    a host). Faster for many hosts with few ports each. Shared semaphore still
    caps total in-flight connections.
    """
    sem = asyncio.Semaphore(config.concurrency)

    async def _one_host(host):
        return host, await scan_host(host, ports, config, sem, on_progress=on_progress)

    pairs = await asyncio.gather(*(_one_host(h) for h in hosts))
    return dict(pairs)
