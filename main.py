import curses
import sys
import firewall
import steam_detect
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

    CYAN = curses.color_pair(1)
    GREEN = curses.color_pair(2)
    RED = curses.color_pair(3)
    YELLOW = curses.color_pair(4)
    WHITE = curses.color_pair(5)
    BTN_ISO = curses.color_pair(6) | curses.A_BOLD
    BTN_REL = curses.color_pair(7) | curses.A_BOLD
    BOLD = curses.A_BOLD

    isolated = False
    steam_running = False
    steam_pid = None

    def refresh():
        nonlocal isolated, steam_running, steam_pid
        pid = steam_detect.find_steam_pid()
        steam_pid = pid
        steam_running = pid is not None
        isolated = firewall.is_active()

    def toggle():
        if isolated:
            firewall.disable()
        else:
            firewall.enable()
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
        put(r, 11, "steam network isolation", WHITE)
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
            put(r, 2, "Network ISOLATED - Steam cannot reach the internet", WHITE)
        else:
            put(r, 0, "○", RED)
            put(r, 2, "Network normal - Steam has full internet access", WHITE)
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

        keys = "SPACE/1 toggle   X/2 force quit   L/3 launch steam   R refresh   Q quit"
        put(h - 1, 0, keys, YELLOW)

        stdscr.refresh()
        key = stdscr.getch()

        if key in (ord("q"), ord("Q")):
            break
        elif key in (ord(" "), ord("1")):
            toggle()
        elif key in (ord("x"), ord("X"), ord("2")):
            steam_detect.kill_steam()
            refresh()
        elif key in (ord("l"), ord("L"), ord("3")):
            steam_detect.launch_steam()
            refresh()
        elif key in (ord("r"), ord("R")):
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
