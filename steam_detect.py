import os
import subprocess
import re

DEFAULT_STEAM_COMMON_DIR = os.path.expanduser("~/Library/Application Support/Steam/steamapps/common")

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
        f"{os.path.expanduser('~')}/Applications/Steam.app",
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None

def kill_steam() -> None:
    subprocess.run(["pkill", "-9", "-f", "MacOS/steam_osx"])
    subprocess.run(["pkill", "-9", "-i", "steam"])

def launch_steam() -> None:
    subprocess.run(["open", "-a", "Steam"])

def get_steam_common_dirs() -> list[str]:
    dirs = [DEFAULT_STEAM_COMMON_DIR]
    vdf_path = os.path.expanduser("~/Library/Application Support/Steam/steamapps/libraryfolders.vdf")
    if os.path.exists(vdf_path):
        try:
            with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            matches = re.findall(r'"path"\s+"([^"]+)"', content)
            for m in matches:
                common_path = os.path.join(m, "steamapps", "common")
                if common_path not in dirs and os.path.exists(common_path):
                    dirs.append(common_path)
        except Exception:
            pass
    return [d for d in dirs if os.path.exists(d)]

def get_installed_games(common_dirs: list[str] | None = None) -> list[dict]:
    if common_dirs is None:
        common_dirs = get_steam_common_dirs()
    
    games = []
    seen_paths = set()

    for common_dir in common_dirs:
        if not os.path.exists(common_dir):
            continue
        try:
            entries = sorted(os.listdir(common_dir), key=lambda s: s.lower())
        except Exception:
            continue

        for item in entries:
            if item.startswith("."):
                continue
            item_path = os.path.join(common_dir, item)
            if not os.path.isdir(item_path):
                continue

            apps = []
            for root, dirs, _ in os.walk(item_path):
                for d in dirs:
                    if d.endswith(".app"):
                        app_full_path = os.path.join(root, d)
                        rel_to_game = os.path.relpath(app_full_path, item_path)
                        apps.append((d[:-4], app_full_path, rel_to_game))
                dirs[:] = [d for d in dirs if not d.endswith(".app")]

            if not apps:
                continue

            def sort_key(app_info):
                name, path, rel = app_info
                depth = rel.count(os.sep)
                clean_item = item.lower().replace(" ", "").replace("_", "").replace("-", "")
                clean_name = name.lower().replace(" ", "").replace("_", "").replace("-", "")
                name_match = 0 if (clean_name in clean_item or clean_item in clean_name) else 1
                return (depth, name_match, name.lower())

            apps.sort(key=sort_key)
            primary_name, primary_path, _ = apps[0]

            if primary_path in seen_paths:
                continue
            seen_paths.add(primary_path)

            games.append({
                "folder_name": item,
                "folder_path": item_path,
                "primary_name": primary_name,
                "primary_app": primary_path,
                "apps": [(a[0], a[1]) for a in apps],
            })

    games.sort(key=lambda g: g["folder_name"].lower())
    return games

def launch_game(app_path: str) -> tuple[bool, str]:
    if not os.path.exists(app_path):
        return False, f"App not found at: {app_path}"
    try:
        proc = subprocess.run(["open", app_path], capture_output=True, text=True)
        if proc.returncode != 0:
            return False, proc.stderr.strip() or f"Exit code {proc.returncode}"
        return True, ""
    except Exception as e:
        return False, str(e)

