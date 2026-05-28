#!/usr/bin/env bash
# Run this ONCE before using SteamVeil for the first time.
# No external dependencies this ONLY uses only Python's built-in curses.

BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
RED="\033[31m"
RESET="\033[0m"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "${BOLD}${CYAN}SteamVeil Setup${RESET}"
echo ""

#check for python
echo "${BOLD}[1/4] Checking Python…${RESET}"
if ! command -v python3 &>/dev/null; then
    echo "${RED}[FAILED] python3 not found. Install it from https://python.org${RESET}"
    exit 1
fi
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "${GREEN}[SUCCESS] Python ${PY_VER} found${RESET}"

echo ""
echo "${BOLD}[2/3]  Setting up passwordless sudo for /etc/hosts management…${RESET}"
echo "(This is how SteamVeil edits /etc/hosts without prompting every time)"
echo "Your admin password is required ${BOLD}once${RESET} here:"
echo ""

SUDOERS_FILE="/etc/sudoers.d/steamveil"
# required things we need are tee /etc/hosts, dscacheutil -flushcache, killall mDNSResponder
SUDOERS_CONTENT="${USER} ALL=(ALL) NOPASSWD: /usr/bin/tee /etc/hosts

${USER} ALL=(ALL) NOPASSWD: /usr/bin/dscacheutil -flushcache
${USER} ALL=(ALL) NOPASSWD: /bin/kill -HUP *
${USER} ALL=(ALL) NOPASSWD: /usr/bin/killall -HUP mDNSResponder"

if sudo test -f "${SUDOERS_FILE}" 2>/dev/null; then
    echo "${GREEN}[SUCCESS] Sudo entry already exists${RESET}"
else
    # validate the content before writing

    echo "${SUDOERS_CONTENT}" | sudo tee "${SUDOERS_FILE}" > /dev/null
    sudo chmod 440 "${SUDOERS_FILE}"

    # if visudo check fails then remove the file

    if ! sudo visudo -c -f "${SUDOERS_FILE}" &>/dev/null; then
        sudo rm -f "${SUDOERS_FILE}"
        echo "${RED}[FAILURE] Sudoers validation failed we removed the bad entry${RESET}"
        echo "You will need to approve sudo prompts manually. If you see this please report it on GitHub issues."
    else
        echo "${GREEN}[SUCCESS] Sudo entry added (/etc/sudoers.d/steamveil)${RESET}"
    fi
fi
# run script executable
echo ""
echo "${BOLD}[3/3]  Finalising…${RESET}"
chmod +x "${SCRIPT_DIR}/run.sh"
echo "${GREEN}[SUCCESS] run.sh is executable${RESET}"

echo ""
echo "${BOLD}${GREEN}[COMPLETE] Setup success!${RESET}"
echo ""
echo "To start SteamVeil, run:"
echo "${BOLD}cd ${SCRIPT_DIR} && ./run.sh${RESET}"
echo "or:"
echo "${BOLD}python3 ${SCRIPT_DIR}/main.py${RESET}"
echo ""
echo "${BOLD}How to use:${RESET}"
echo "Press SPACE or '1' to ISOLATE Steam and restrict its internet access"
echo "Then press 'x' or '2' to heavy quit steam"
echo "Lastly open your game and play even when someone else in your steam family is playing!"


echo ""
