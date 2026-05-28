import subprocess
import os
# fix
HOSTS_FILE = "/etc/hosts"
MARKER_START = "# ======= SteamVeil START ======="
MARKER_END   = "# ======= SteamVeil END ======="
# this should be all
STEAM_DOMAINS = [
    "steampowered.com",
    "store.steampowered.com",
    "api.steampowered.com",
    "login.steampowered.com",
    "steamlogin.steampowered.com",
    "checkout.steampowered.com",
    "help.steampowered.com",
    "partner.steampowered.com",
    "steamcommunity.com",
    "steamgames.com",
    "steamstatic.com",
    "steamcontent.com",
    "cs.steampowered.com",
    "cm.steampowered.com",
    "client-update.steampowered.com",
    "cdn.steamstatic.com",
    "media.steampowered.com",
    "valvesoftware.com",
]

def _read_hosts() -> str:
    with open(HOSTS_FILE, "r") as f:
        return f.read()

def _write_hosts(content: str) -> tuple[bool, str]:
    proc = subprocess.run(
        ["sudo", "tee", HOSTS_FILE],
        input=content,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        return False, proc.stderr.strip()
    return True, ""
#kill
def _flush_dns() -> None:
    subprocess.run(["sudo", "dscacheutil", "-flushcache"], capture_output=True)
    subprocess.run(["sudo", "killall", "-HUP", "mDNSResponder"], capture_output=True)

def _build_block() -> str:
    lines = [MARKER_START]
    for domain in STEAM_DOMAINS:
        lines.append(f"127.0.0.1  {domain}")
    lines.append(MARKER_END)
    return "\n".join(lines)

def enable() -> tuple[bool, str]:
    content = _read_hosts()
    if MARKER_START in content:
        return True, "already active"

    new_content = content.rstrip() + "\n\n" + _build_block() + "\n"
    ok, err = _write_hosts(new_content)
    if ok:
        _flush_dns()
    return ok, err

def disable() -> tuple[bool, str]:
    content = _read_hosts()
    if MARKER_START not in content:
        return True, "already inactive"

    lines = content.splitlines()
    new_lines = []
    inside = False
    for line in lines:
        if line.strip() == MARKER_START:
            inside = True
            continue
        if line.strip() == MARKER_END:
            inside = False
            continue
        if not inside:
            new_lines.append(line)

    new_content = "\n".join(new_lines).rstrip() + "\n"
    ok, err = _write_hosts(new_content)
    if ok:
        _flush_dns()
    return ok, err

def is_active() -> bool:
    try:
        return MARKER_START in _read_hosts()
    except Exception:
        return False

def fix_hosts() -> tuple[bool, str]:
    content = _read_hosts()
    lines = content.splitlines()
    new_lines = []
    inside = False
    for line in lines:
        if "======= SteamGuard START" in line or "======= SteamVeil START" in line:
            inside = True
            continue
        if "======= SteamGuard END" in line or "======= SteamVeil END" in line:
            inside = False
            continue
        if not inside:
            new_lines.append(line)

    new_content = "\n".join(new_lines).rstrip() + "\n"
    ok, err = _write_hosts(new_content)
    if ok:
        _flush_dns()
    return ok, err
