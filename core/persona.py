#!/usr/bin/env python3
"""
persona.py – tumhara personal cyber‑coach, full‑on personality mode.
Add lines, tweak sarcasm, and watch your terminal feel like a cyber‑cafe.
"""

import random
import argparse
import datetime
import logging
import os

# ---- 1. Personality pool (mix of wit, tech, and a tad of drama) ----
DEFAULT_PERSONALITY = [
    "Bhai, yeh alert? Shayd koi hacker ne Wi‑Fi speed se speed rakhi 😜",
    "Logs ko padhte hue chai ka cup bhi pee lo – #StayHydrated",
    "Firewall? Woh mere ghar ka guard hai – door kharaab hua, toh log ghus jaate 😱",
    "SQLi ka joke: \"admin' OR '1'='1 --\" – bas, koi bhi login kar sakta! 🔥",
    "Logs mein drama: ek command – `grep 'Failed password' auth.log` – aur real‑time drama shuru!",
    "Mere pass ek kahani hai: ek attacker ne 0‑day ka istemal kiya, aur main ne `pwned` ke saath block kar diya! 💪"
]

# ---- 2. Optional user‑added lines (from an external file) ----
USER_LINES_FILE = "my_personalities.txt"

def load_user_personalities() -> list:
    """Load lines from a user‑supplied text file, one per line."""
    if not os.path.exists(USER_LINES_FILE):
        return []
    with open(USER_LINES_FILE, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# ---- 3. Logging – so we can see when we shout out sarcastic lines ----
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S"
)

def shout(line: str):
    """Print the line and log it – because we like to brag on the console."""
    print(line)
    logging.info(line)

# ---- 4. Main CLI logic ----
def main():
    parser = argparse.ArgumentParser(
        description="Tumhara cyber‑coach – random or custom, with a sprinkle of roast."
    )
    parser.add_argument("--random", action="store_true",
                        help="Print a random line from personality pool.")
    parser.add_argument("--list", action="store_true",
                        help="List all available personality lines.")
    parser.add_argument("--add", metavar="LINE", type=str,
                        help="Add a new line to the pool (and save to file).")
    parser.add_argument("--help-persona", action="store_true",
                        help="Show how to customize your own lines.")
    args = parser.parse_args()

    # Load the personality list
    personality = DEFAULT_PERSONALITY + load_user_personalities()

    if args.help_persona:
        print("""
How to add your own lines to 'persona.py':
1. Run: `./persona.py --add "Your custom witty line here"`
2. The line will be appended to 'my_personalities.txt'.
3. Restart the script to see it in action.
Enjoy crafting your own cyber‑meme style!
""")
        return

    if args.add:
        # Append to file
        with open(USER_LINES_FILE, "a", encoding="utf-8") as f:
            f.write(args.add.strip() + "\n")
        print(f"Added new line to {USER_LINES_FILE}. Reload and enjoy!")
        return

    if args.list:
        print("Current personality pool:")
        for idx, line in enumerate(personality, 1):
            print(f"{idx}. {line}")
        return

    # Default or random output
    if args.random:
        shout(random.choice(personality))
    else:
        shout("Yo, main tumhara cyber‑coach hoon. Chal, kaun se logs ko dekhna hai?")

if __name__ == "__main__":
    main()
