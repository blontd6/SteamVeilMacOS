import curses
import sys
import firewall
import steam_detect

def select_and_launch_game(stdscr, colors):
    CYAN, GREEN, RED, YELLOW, WHITE, BTN_ISO, BTN_REL, BOLD, BTN_CYAN = colors
    
    stdscr.timeout(-1)
    games = steam_detect.get_installed_games()
    selected_idx = 0

    if not games:
        while True:
            stdscr.erase()
            h, w = stdscr.getmaxyx()
            
            def put(row, col, text, attr=WHITE, trunc=True):
                if row >= h - 1 or row < 0:
                    return
                if trunc:
                    text = text[: max(0, w - col - 1)]
                try:
                    stdscr.addstr(row, col, text, attr)
                except curses.error:
                    pass

            put(1, 0, "SteamVeil > Run Game Directly", CYAN | BOLD)
            put(3, 0, "No installed games (.app) found in:", RED | BOLD)
            put(4, 2, steam_detect.DEFAULT_STEAM_COMMON_DIR, WHITE)
            put(6, 0, "Make sure your Steam games are installed.", YELLOW)
            put(h - 2, 0, "Press any key or ESC to return...", CYAN)
            stdscr.refresh()
            stdscr.getch()
            stdscr.timeout(3000)
            return False, "No installed games found"

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        def put(row, col, text, attr=WHITE, trunc=True):
            if row >= h - 1 or row < 0:
                return
            if trunc:
                text = text[: max(0, w - col - 1)]
            try:
                stdscr.addstr(row, col, text, attr)
            except curses.error:
                pass

        put(1, 0, "SteamVeil", CYAN | BOLD)
        put(1, 11, "> Launch Game Directly", WHITE | BOLD)
        put(2, 0, f"Found {len(games)} installed game(s) in Steam common folder", WHITE)

        header_rows = 4
        footer_rows = 3
        max_visible_items = max(1, h - header_rows - footer_rows)

        if selected_idx < 0:
            selected_idx = 0
        elif selected_idx >= len(games):
            selected_idx = len(games) - 1

        scroll_offset = 0
        if selected_idx >= max_visible_items:
            scroll_offset = selected_idx - max_visible_items + 1

        visible_games = games[scroll_offset : scroll_offset + max_visible_items]

        for i, game in enumerate(visible_games):
            idx = scroll_offset + i
            row = header_rows + i
            is_selected = (idx == selected_idx)
            
            prefix = " ▸ " if is_selected else "   "
            game_title = game["folder_name"]
            app_name = f"({game['primary_name']}.app)" if game["primary_name"].lower() != game["folder_name"].lower() else ""
            line_str = f"{prefix}{idx + 1:2d}. {game_title} {app_name}".rstrip()

            if is_selected:
                put(row, 0, line_str, BTN_CYAN)
            else:
                put(row, 0, line_str, WHITE)

        footer_keys = "ENTER/SPACE launch   UP/DOWN navigate   ESC/Q back"
        put(h - 2, 0, footer_keys, YELLOW)

        stdscr.refresh()
        key = stdscr.getch()

        if key in (27, ord("q"), ord("Q"), ord("b"), ord("B")):
            stdscr.timeout(3000)
            return False, "Cancelled game launch"
        elif key in (curses.KEY_UP, ord("k"), ord("K")):
            selected_idx = max(0, selected_idx - 1)
        elif key in (curses.KEY_DOWN, ord("j"), ord("J")):
            selected_idx = min(len(games) - 1, selected_idx + 1)
        elif key == curses.KEY_PPAGE:
            selected_idx = max(0, selected_idx - max_visible_items)
        elif key == curses.KEY_NPAGE:
            selected_idx = min(len(games) - 1, selected_idx + max_visible_items)
        elif key == curses.KEY_HOME:
            selected_idx = 0
        elif key == curses.KEY_END:
            selected_idx = len(games) - 1
        elif key in (ord("\n"), ord("\r"), curses.KEY_ENTER, 10, 13, ord(" ")):
            selected_game = games[selected_idx]
            ok, err = steam_detect.launch_game(selected_game["primary_app"])
            stdscr.timeout(3000)
            if ok:
                return True, f"Launched {selected_game['folder_name']} directly"
            else:
                return False, f"Error launching {selected_game['folder_name']}: {err}"
        elif key == curses.KEY_RESIZE:
            pass

# all the pretty stuff
def run(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    stdscr.timeout(3000)

    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_RED, -1)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)
    curses.init_pair(5, curses.COLOR_WHITE, -1)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_CYAN)

    CYAN = curses.color_pair(1)
    GREEN = curses.color_pair(2)
    RED = curses.color_pair(3)
    YELLOW = curses.color_pair(4)
    WHITE = curses.color_pair(5)
    BTN_ISO = curses.color_pair(6) | curses.A_BOLD
    BTN_REL = curses.color_pair(7) | curses.A_BOLD
    BTN_CYAN = curses.color_pair(8) | curses.A_BOLD
    BOLD = curses.A_BOLD

    colors = (CYAN, GREEN, RED, YELLOW, WHITE, BTN_ISO, BTN_REL, BOLD, BTN_CYAN)

    isolated = False
    steam_running = False
    steam_pid = None
    last_action_msg = ""

    def refresh():
        nonlocal isolated, steam_running, steam_pid
        pid = steam_detect.find_steam_pid()
        steam_pid = pid
        steam_running = pid is not None
        isolated = firewall.is_active()

    def toggle():
        nonlocal last_action_msg
        if isolated:
            ok, err = firewall.disable()
            last_action_msg = "Released Steam network" if ok else f"Error: {err}"
        else:
            ok, err = firewall.enable()
            last_action_msg = "Isolated Steam network" if ok else f"Error: {err}"
        refresh()

    refresh()

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        def put(row, col, text, attr=WHITE, trunc=True):
            if row >= h - 1:
                return
            if trunc:
                text = text[: w - col - 1]
            try:
                stdscr.addstr(row, col, text, attr)
            except curses.error:
                pass

        r = 1

        put(r, 0, "SteamVeil", CYAN | BOLD)
        put(r, 11, "steam network isolation - by blon", WHITE)
        r += 2

        put(r, 0, "STATUS", BOLD)
        r += 1

        if steam_running:
            put(r, 0, "●", GREEN)
            put(r, 2, f"Steam running   pid {steam_pid}", WHITE)
        else:
            put(r, 0, "○", RED)
            put(r, 2, "Steam not detected", WHITE)
        r += 1

        if isolated:
            put(r, 0, "●", GREEN)
            put(r, 2, "Network ISOLATED Steam cannot reach the internet", WHITE)
        else:
            put(r, 0, "○", RED)
            put(r, 2, "Network normal Steam has full internet access", WHITE)
        r += 2

        if isolated:
            btn = "RELEASE STEAM"
            put(r, 0, btn, BTN_REL)
        else:
            btn = "ISOLATE STEAM"
            put(r, 0, btn, BTN_ISO)
        put(r, len(btn) + 2, "press SPACE or 1", YELLOW)
        r += 2

        btn_fq = "FORCE QUIT STEAM"
        put(r, 0, btn_fq, BTN_REL)
        put(r, len(btn_fq) + 2, "press X or 2", YELLOW)
        r += 2

        btn_launch = "LAUNCH STEAM"
        put(r, 0, btn_launch, BTN_ISO)
        put(r, len(btn_launch) + 2, "press L or 3", YELLOW)
        r += 2

        btn_fix = "FIX HOSTS"
        put(r, 0, btn_fix, BTN_REL)
        put(r, len(btn_fix) + 2, "press 4", YELLOW)
        r += 2

        btn_game = "RUN GAME DIRECT"
        put(r, 0, btn_game, BTN_CYAN)
        put(r, len(btn_game) + 2, "press G or 5", YELLOW)
        r += 2

        if isolated:
            put(r, 0, "BLOCKING", BOLD)
            r += 1
            blocked = [
                "steampowered.com  api.steampowered.com  login.steampowered.com",
                "steamcommunity.com  steamcontent.com  cm.steampowered.com  (+more)",
                "Your Mac's internet is fully active.",
            ]
            for line in blocked:
                put(r, 0, line, WHITE)
                r += 1
            r += 1

        keys = "SPACE/1 toggle   X/2 force quit   L/3 launch steam   4 fix hosts   G/5 run game   R refresh   Q quit"
        if last_action_msg:
            put(h - 3, 0, f"> {last_action_msg}", CYAN)
        put(h - 1, 0, keys, YELLOW)

        stdscr.refresh()
        key = stdscr.getch()

        if key in (ord("q"), ord("Q")):
            break
        elif key in (ord(" "), ord("1")):
            toggle()
        elif key in (ord("x"), ord("X"), ord("2")):
            steam_detect.kill_steam()
            last_action_msg = "Force quit Steam"
            refresh()
        elif key in (ord("l"), ord("L"), ord("3")):
            steam_detect.launch_steam()
            last_action_msg = "Launched Steam"
            refresh()
        elif key == ord("4"):
            ok, err = firewall.fix_hosts()
            last_action_msg = "Fixed hosts file and flushed DNS" if ok else f"Fix hosts error: {err}"
            refresh()
        elif key in (ord("g"), ord("G"), ord("5")):
            _, msg = select_and_launch_game(stdscr, colors)
            if msg:
                last_action_msg = msg
            refresh()
        elif key in (ord("r"), ord("R")):
            last_action_msg = "Refreshed status"
            refresh()
        elif key == curses.KEY_RESIZE:
            pass
        else:
            refresh()

def main():
    try:
        curses.wrapper(run)
    except KeyboardInterrupt:
        pass
    sys.stdout.write("\033[?25h")
    print("SteamVeil closed.")

if __name__ == "__main__":
    main()

