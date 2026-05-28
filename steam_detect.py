import subprocess
import re

def find_steam_pid() -> int | None:
    try:
        result = subprocess.run(
            ["pgrep", "-f", "MacOS/steam_osx"],
            capture_output=True, text=True,
        )
        pids = [p.strip() for p in result.stdout.strip().splitlines() if p.strip()]
        if pids:
            return int(pids[0])

        result = subprocess.run(
            ["pgrep", "-i", "steam"],
            capture_output=True, text=True,
        )
        pids = [p.strip() for p in result.stdout.strip().splitlines() if p.strip()]
        if pids:
            return int(pids[0])
    except Exception:
        pass
    return None

def is_running() -> bool:
    return find_steam_pid() is not None

def get_steam_app_path() -> str | None:
    common_paths = [
        "/Applications/Steam.app",
        "/Applications/Utilities/Steam.app",
        f"{__import__('os').path.expanduser('~')}/Applications/Steam.app",
    ]
    for path in common_paths:
        if __import__('os').path.exists(path):
            return path
    return None

def kill_steam() -> None:
    subprocess.run(["pkill", "-9", "-f", "MacOS/steam_osx"])
    subprocess.run(["pkill", "-9", "-i", "steam"])

def launch_steam() -> None:
    subprocess.run(["open", "-a", "Steam"])
