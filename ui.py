"""
ui.py - Futuristic terminal UI for DeerTheGreat.
Pure ANSI escape codes, no external dependencies (works in Windows Terminal,
modern cmd.exe, PowerShell, and any Linux terminal).
"""

import os
import shutil
import sys
import time

# ---- enable ANSI on legacy Windows consoles -------------------------------
if os.name == "nt":
    os.system("")  # this one call flips on VT100 processing in cmd.exe


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[38;5;51m"
    GREEN = "\033[38;5;46m"
    RED = "\033[38;5;196m"
    YELLOW = "\033[38;5;220m"
    MAGENTA = "\033[38;5;201m"
    BLUE = "\033[38;5;27m"
    GREY = "\033[38;5;240m"
    WHITE = "\033[38;5;255m"


_DEER_OPEN = [
    "⠀⠀⠀⠀⠀⣠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠈⠻⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⡿⠋⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠈⠻⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⡿⠋⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⣠⡀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⣠⡀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠈⠙⠿⣷⣼⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣴⡿⠟⠉⠀⠀⠀⠀⠀⠀⠀",
    "⠀⡀⠀⠀⠀⠀⠀⠀⠀⠈⠙⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡟⠉⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀",
    "⠀⢹⣦⡀⠀⠀⠀⠀⠀⠀⠀⢹⣷⠀⠀⠀⠀⣀⣀⣠⣤⣤⣦⣤⣤⣀⣀⡀⠀⠀⠀⢰⣿⠁⠀⠀⠀⠀⠀⠀⠀⣠⣾⠁⠀",
    "⠀⠀⢻⣿⣦⡀⠀⠀⠀⠀⠀⣨⣿⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣾⣯⡀⠀⠀⠀⠀⠀⣠⣾⣿⠃⠀⠀",
    "⠀⠀⠈⣿⣿⣿⣦⡀⠀⢀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣄⠀⠀⣠⣾⣿⣿⡏⠀⠀⠀",
    "⠀⠀⠀⠸⣿⣿⡿⢁⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠹⣿⣿⡿⠀⠀⠀⠀",
    "⠀⠀⠀⠀⢹⣿⣣⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣻⣿⠁⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠃⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠋⠉⠛⣿⣿⣿⣿⣿⣿⡟⠋⠉⠛⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠃⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀⣸⣿⣿⣿⣿⣿⡀⠀⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣤⣶⣿⣿⣿⣿⣿⣿⣷⣦⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣭⣭⣭⣭⣭⣭⣽⣿⣿⣿⣿⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠻⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠛⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⠻⠿⡿⠿⠛⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
]

_DEER_CLOSED = [
    _DEER_OPEN[0], _DEER_OPEN[1], _DEER_OPEN[2], _DEER_OPEN[3], _DEER_OPEN[4],
    _DEER_OPEN[5], _DEER_OPEN[6], _DEER_OPEN[7], _DEER_OPEN[8], _DEER_OPEN[9],
    _DEER_OPEN[10], _DEER_OPEN[11], _DEER_OPEN[12],
    "⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣏⣉⣉⣉⣉⣹⣿⣿⣿⣿⣿⣉⣉⣉⣉⣉⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀",
    _DEER_OPEN[14], _DEER_OPEN[15], _DEER_OPEN[16], _DEER_OPEN[17], _DEER_OPEN[18],
    _DEER_OPEN[19], _DEER_OPEN[20], _DEER_OPEN[21], _DEER_OPEN[22],
]

_DEER_BLANK_LINE = " " * len(_DEER_OPEN[0])
_DEER_WIDTH = len(_DEER_OPEN[0])
_DEER_HEIGHT = len(_DEER_OPEN)

BANNER = f"""
{C.CYAN}{chr(10).join(_DEER_OPEN)}{C.RESET}
{C.BOLD}{C.WHITE}              DEERTHEGREAT{C.RESET}
{C.GREY}           network port scanner{C.RESET}
"""

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


def term_width(default=100):
    return shutil.get_terminal_size((default, 24)).columns


def _reveal_frame(rows_visible: int) -> list:
    """Progressively 'materialize' the dot-matrix deer from top to bottom."""
    visible = _DEER_OPEN[:rows_visible]
    hidden = [_DEER_BLANK_LINE] * (_DEER_HEIGHT - rows_visible)
    return visible + hidden


def print_banner(version="0.04"):
    """Animated startup: the dot-matrix deer materializes top-down, blinks twice,
    then the name types out. Falls back to a plain static print when output
    isn't an interactive terminal (e.g. piped to a file), so logs stay clean.
    """
    if not sys.stdout.isatty():
        print(BANNER)
        print(f"{C.GREY}  v{version} | stdlib-only | async TCP connect scanner{C.RESET}\n")
        return

    print()  # leading blank line to match static BANNER spacing

    # Stage 1: materialize top-down, a few rows at a time.
    step = 3
    reveal_points = list(range(step, _DEER_HEIGHT, step)) + [_DEER_HEIGHT]
    for i, rows_visible in enumerate(reveal_points):
        if i > 0:
            sys.stdout.write(f"\033[{_DEER_HEIGHT}A")
        for line in _reveal_frame(rows_visible):
            sys.stdout.write(f"\033[K{C.CYAN}{line}{C.RESET}\n")
        sys.stdout.flush()
        time.sleep(0.045)

    # Stage 2: blink twice.
    blink_sequence = [_DEER_CLOSED, _DEER_OPEN, _DEER_CLOSED, _DEER_OPEN]
    blink_delays = [0.09, 0.12, 0.09, 0.12]
    for frame, delay in zip(blink_sequence, blink_delays):
        sys.stdout.write(f"\033[{_DEER_HEIGHT}A")
        for line in frame:
            sys.stdout.write(f"\033[K{C.CYAN}{line}{C.RESET}\n")
        sys.stdout.flush()
        time.sleep(delay)

    # Stage 3: type out the name underneath.
    label = "DEERTHEGREAT"
    sys.stdout.write(f"{C.BOLD}{C.WHITE}              ")
    sys.stdout.flush()
    for ch in label:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(0.02)
    sys.stdout.write(f"{C.RESET}\n")
    print(f"{C.GREY}           network port scanner{C.RESET}\n")
    print(f"{C.GREY}  v{version} | stdlib-only | async TCP connect scanner{C.RESET}\n")


def print_scan_header(target_count, port_count, concurrency, timeout):
    print(f"{C.BLUE}┌─ Scan Configuration {'─' * (term_width() - 22)}{C.RESET}")
    print(f"{C.BLUE}│{C.RESET} Targets     : {C.WHITE}{target_count}{C.RESET}")
    print(f"{C.BLUE}│{C.RESET} Ports each  : {C.WHITE}{port_count}{C.RESET}")
    print(f"{C.BLUE}│{C.RESET} Concurrency : {C.WHITE}{concurrency}{C.RESET}")
    print(f"{C.BLUE}│{C.RESET} Timeout     : {C.WHITE}{timeout}s{C.RESET}")
    print(f"{C.BLUE}└{'─' * (term_width() - 1)}{C.RESET}\n")


class LiveProgress:
    """A single-line, in-place-updating progress bar with spinner + ETA."""

    def __init__(self, total, label="Scanning"):
        self.total = max(total, 1)
        self.done = 0
        self.open_found = 0
        self.label = label
        self.start = time.time()
        self._frame = 0
        self._last_len = 0

    def update(self, done_delta=1, open_delta=0):
        self.done += done_delta
        self.open_found += open_delta
        self._render()

    def _render(self):
        pct = self.done / self.total
        width = min(30, max(10, term_width() - 60))
        filled = int(width * pct)
        bar = f"{C.GREEN}{'━' * filled}{C.GREY}{'━' * (width - filled)}{C.RESET}"
        elapsed = time.time() - self.start
        rate = self.done / elapsed if elapsed > 0 else 0
        eta = (self.total - self.done) / rate if rate > 0 else 0
        spinner = SPINNER_FRAMES[self._frame % len(SPINNER_FRAMES)]
        self._frame += 1

        line = (
            f"\r{C.CYAN}{spinner}{C.RESET} {self.label} [{bar}] "
            f"{C.WHITE}{pct * 100:5.1f}%{C.RESET} "
            f"({self.done}/{self.total})  "
            f"{C.GREEN}open:{self.open_found}{C.RESET}  "
            f"{C.GREY}eta {eta:4.0f}s{C.RESET}"
        )
        pad = max(0, self._last_len - len(line))
        sys.stdout.write(line + " " * pad)
        sys.stdout.flush()
        self._last_len = len(line)

    def finish(self):
        elapsed = time.time() - self.start
        sys.stdout.write("\r" + " " * (self._last_len + 2) + "\r")
        print(
            f"{C.GREEN}✔{C.RESET} {self.label} complete "
            f"{C.GREY}({self.done} checked, {elapsed:.1f}s elapsed){C.RESET}\n"
        )


def print_host_result(host, open_ports_data):
    """
    open_ports_data: list of dicts {port, service, banner}
    """
    print(f"{C.MAGENTA}┌─ {C.BOLD}{host}{C.RESET}{C.MAGENTA} {'─' * max(1, term_width() - len(host) - 5)}{C.RESET}")
    if not open_ports_data:
        print(f"{C.GREY}│  no open ports found{C.RESET}")
    else:
        print(f"{C.BLUE}│  {'PORT':<8}{'SERVICE':<20}{'BANNER'}{C.RESET}")
        for entry in open_ports_data:
            port = entry["port"]
            svc = entry["service"]
            banner = entry.get("banner", "") or ""
            banner_display = (banner[:60] + "...") if len(banner) > 60 else banner
            print(
                f"{C.BLUE}│  {C.GREEN}{port:<8}{C.RESET}{C.WHITE}{svc:<20}{C.RESET}"
                f"{C.GREY}{banner_display}{C.RESET}"
            )
    print(f"{C.MAGENTA}└{'─' * (term_width() - 1)}{C.RESET}")


def print_summary(results, elapsed):
    total_open = sum(len(v) for v in results.values())
    hosts_up = sum(1 for v in results.values() if v)
    print(f"\n{C.CYAN}{C.BOLD}== Summary =={C.RESET}")
    print(f"  Hosts scanned : {len(results)}")
    print(f"  Hosts with open ports : {C.GREEN}{hosts_up}{C.RESET}")
    print(f"  Total open ports : {C.GREEN}{total_open}{C.RESET}")
    print(f"  Elapsed : {elapsed:.2f}s\n")


def error(msg):
    print(f"{C.RED}{C.BOLD}[!] {msg}{C.RESET}", file=sys.stderr)


def info(msg):
    print(f"{C.CYAN}[*]{C.RESET} {msg}")


def warn(msg):
    print(f"{C.YELLOW}[!]{C.RESET} {msg}")
