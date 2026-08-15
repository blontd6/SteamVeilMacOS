# SteamVeil

A simple terminal app that isolates Steam from the network so multiple family members can play shared games simultaneously.

## Setup

Run this **once** to configure permissions:
```bash
sh setup.sh
```

## Usage

Launch the app:
```bash
./run.sh
```

### Controls
Inside the app, you can use these keys:
- **`SPACE` or `1`**: Isolate / Release Steam network access
- **`X` or `2`**: Force quit Steam
- **`L` or `3`**: Launch Steam
- **`4`**: Fix hosts file & flush DNS
- **`G` or `5`**: Run game directly from Steam common directory
- **`R`**: Refresh status
- **`Q`**: Quit SteamVeil

### How to Play Simultaneously
1. Press `SPACE` in SteamVeil to **ISOLATE** Steam
2. Force quit & relaunch Steam (or run your game directly with `G` / `5`)
3. Open your steamshared game 


---------
Please star this repo ⭐

