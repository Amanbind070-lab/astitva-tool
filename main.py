#!/data/user/0/com.termux/files/usr/bin/python3
"""
╔══════════════════════════════════════════════╗
║        ASTITVA MODDING TOOL v4.3             ║
║        Made by: Astitva                      ║
║        All Rights Reserved                   ║
╚══════════════════════════════════════════════╝

Modes:
  - OBB MODE
  - PAK MODE
  - EXTRA FEATURES
"""

import os
import sys
import subprocess
import time
import shutil
import tempfile
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.columns import Columns
import requests
import base64

console = Console(style="bold")

# ==============================================================================
# ★ CONFIG — Sirf yahan apna GitHub info daalo ★
# ==============================================================================
GITHUB_USERNAME = "YOUR_GITHUB_USERNAME"   # ← apna GitHub username yahan daalo
GITHUB_REPO     = "YOUR_REPO_NAME"         # ← apna repo name yahan daalo
GITHUB_BRANCH   = "main"
GITHUB_TOKEN    = "YOUR_GITHUB_TOKEN"      # ← apna GitHub token yahan daalo
# ==============================================================================

# Vibrant color scheme
COLOR_SCHEME = [
    ("bright_red",     "white"),
    ("bright_green",   "yellow"),
    ("bright_blue",    "white"),
    ("bright_yellow",  "red"),
    ("bright_magenta", "cyan"),
    ("bright_cyan",    "magenta"),
    ("red",            "white"),
    ("green",          "yellow"),
    ("blue",           "white"),
    ("yellow",         "red"),
    ("magenta",        "cyan"),
    ("cyan",           "magenta"),
]

# ------------------------------------------------------------------------------
# GitHub Functions
# ------------------------------------------------------------------------------
def get_file_from_github(filepath):
    """Fetch file content from your GitHub repo"""
    try:
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        api_url = (
            f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}"
            f"/contents/{filepath}?ref={GITHUB_BRANCH}"
        )
        console.print(f"[yellow]Fetching {filepath}...[/]")
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        json_response = response.json()
        encoding = json_response.get("encoding")

        if encoding == "base64":
            return base64.b64decode(json_response["content"])
        elif "download_url" in json_response:
            dl = requests.get(json_response["download_url"])
            dl.raise_for_status()
            return dl.content
        else:
            raise Exception(f"Unexpected response: {json_response}")

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Network error: {e}[/]")
        raise
    except Exception as e:
        console.print(f"[red]GitHub error: {e}[/]")
        raise


def get_last_update_time(filepath):
    """Get last commit date for a file"""
    try:
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        url = (
            f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}"
            f"/commits?path={filepath}&sha={GITHUB_BRANCH}&per_page=1"
        )
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        commits = response.json()

        if not commits:
            raise Exception("No commits found")

        commit_date = commits[0]["commit"]["committer"]["date"]
        console.print(f"[green]Last update: {commit_date} UTC[/]")
        return commit_date

    except Exception as e:
        console.print(f"[red]Error getting update time: {e}[/]")
        raise


# ------------------------------------------------------------------------------
# Installation & Setup
# ------------------------------------------------------------------------------
def install_requirements():
    """Install all required system and Python packages"""
    try:
        console.print(Panel(
            ":gear: [bold bright_cyan]Checking System Requirements[/]",
            border_style="bright_green"
        ))

        # System packages
        packages = [
            "wget", "unzip", "zip", "pv", "figlet", "toilet",
            "vim", "curl", "rsync", "unrar", "python", "git"
        ]
        for pkg in packages:
            try:
                result = subprocess.run(
                    ["dpkg-query", "-W", "--showformat=${Status}", pkg],
                    capture_output=True, text=True
                )
                if "install ok installed" not in result.stdout:
                    console.print(f"[yellow]Installing {pkg}...[/]")
                    subprocess.run(["pkg", "install", pkg, "-y"], check=True)
                    console.print(f"[green]{pkg} installed ✓[/]")
                else:
                    console.print(f"[bright_blue]{pkg} already installed[/]")
            except subprocess.CalledProcessError as e:
                console.print(f"[red]Error installing {pkg}: {e}[/]")

        # Python packages
        python_packages = ["rich", "colorama", "termcolor", "requests"]
        pip_cmd = (
            "pip"
            if subprocess.run(["pip", "--version"], capture_output=True).returncode == 0
            else "pip3"
        )
        for pypkg in python_packages:
            try:
                subprocess.run(
                    [pip_cmd, "show", pypkg], check=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                console.print(f"[bright_blue]{pypkg} already installed[/]")
            except subprocess.CalledProcessError:
                console.print(f"[yellow]Installing {pypkg}...[/]")
                subprocess.run([pip_cmd, "install", pypkg], check=True)
                console.print(f"[green]{pypkg} installed ✓[/]")

        # QuickBMS
        def quickbms_installed():
            base = "/data/data/com.termux/files/usr/share/quickbms"
            return (
                os.path.isfile(os.path.join(base, "quickbms")) and
                os.path.isfile(os.path.join(base, "quickbms_4gb_files"))
            )

        if quickbms_installed() or (
            shutil.which("quickbms") and shutil.which("quickbms_4gb_files")
        ):
            console.print("[bright_blue]QuickBMS already present[/]")
        else:
            console.print("[bright_green]Installing QuickBMS...[/]")
            tmp = tempfile.mkdtemp(prefix="qbms_")
            try:
                subprocess.run(
                    ["wget", "http://aluigi.altervista.org/papers/quickbms_linux.zip"],
                    cwd=tmp, check=True
                )
                subprocess.run(["unzip", "-o", "quickbms_linux.zip"], cwd=tmp, check=True)

                home_dir = os.path.expanduser("~/quickbms")
                if os.path.exists(home_dir):
                    shutil.rmtree(home_dir)
                os.makedirs(home_dir)

                for exe in ("quickbms", "quickbms_4gb_files"):
                    src = os.path.join(tmp, exe)
                    dst = os.path.join(home_dir, exe)
                    shutil.copy2(src, dst)
                    os.chmod(dst, 0o755)

                share = "/data/data/com.termux/files/usr/share/quickbms"
                if os.path.isdir(share):
                    shutil.rmtree(share)
                shutil.move(home_dir, share)
                console.print(f"[green]QuickBMS installed to {share} ✓[/]")
            finally:
                shutil.rmtree(tmp)

        # Download mod files from GitHub
        files_to_download = {
            "DARKSIDE":      ("DARKSIDE",       "$HOME/DARK_PAK/DARKSIDE",   True),
            "repak.bms":     ("repak.bms",       "$HOME/repak.bms",           False),
            "FILES_OBB.rar": ("FILES_OBB.rar",   "$HOME/DARK_PAK/FILES_OBB.rar", False),
            "pakskin":       ("pakskin",          "$HOME/pakskin",             True),
        }
        os.makedirs(os.path.expandvars("$HOME/DARK_PAK"), exist_ok=True)

        for filename, (filepath, dest_template, is_executable) in files_to_download.items():
            dest = os.path.expandvars(dest_template)
            try:
                console.print(f"[yellow]Downloading {filename}...[/]")
                file_data = get_file_from_github(filepath)

                mode = "wb"
                with open(dest, mode) as f:
                    f.write(file_data if isinstance(file_data, bytes)
                            else file_data.encode("utf-8"))

                if is_executable:
                    os.chmod(dest, 0o755)
                console.print(f"[green]{filename} saved ✓[/]")

                # FILES_OBB.rar extraction prompt
                if filename == "FILES_OBB.rar":
                    while True:
                        choice = Prompt.ask(
                            "[yellow]Extract FILES_OBB.rar? (y=yes / n=no / c=check update)[/]"
                        ).strip().lower()
                        if choice == "y":
                            if subprocess.run(
                                ["unrar"], stdout=subprocess.PIPE
                            ).returncode != 0:
                                subprocess.run(["pkg", "install", "unrar", "-y"], check=True)
                            subprocess.run(
                                ["unrar", "x", "-o+", dest, "/storage/emulated/0"],
                                check=True
                            )
                            console.print("[green]Extraction done ✓[/]")
                            break
                        elif choice == "n":
                            console.print("[yellow]Skipping extraction[/]")
                            break
                        elif choice == "c":
                            get_last_update_time(filepath)
                        else:
                            console.print("[red]Invalid input[/]")

            except Exception as e:
                console.print(f"[red]Failed to process {filename}: {e}[/]")
                continue

        console.print(Panel(
            ":white_check_mark: [bold bright_green]SETUP COMPLETED SUCCESSFULLY[/]",
            border_style="bright_green"
        ))

    except Exception as e:
        console.print(f"[red]Fatal error during installation: {e}[/]")
        sys.exit(1)


# ------------------------------------------------------------------------------
# Welcome Screen — No verification, fully open
# ------------------------------------------------------------------------------
def welcome_screen():
    try:
        now = datetime.now().strftime("%d-%m-%Y | %H:%M:%S")

        title_panel = Panel(
            Text("ASTITVA MODDING TOOL", style="bold white on purple"),
            title=":rocket: Premium Modding Tool v4.3",
            subtitle="Made with :heart: by Astitva",
            border_style="bright_magenta"
        )

        user_info = Text.assemble(
            ("⏰ Time : ", "bold underline bright_cyan"),
            (f"{now}\n",   "bold italic bright_magenta"),
            ("🗣️  Dev  : ", "bold underline bright_cyan"),
            ("Astitva",    "bold italic bright_magenta"),
        )

        with console.screen() as screen:
            screen.update(title_panel)
            time.sleep(1)
            screen.update(Panel(
                user_info, border_style="bright_magenta", title=":star: Info"
            ))
            time.sleep(1)
            screen.update(Panel(
                "✅ Welcome, Astitva! Tool is Ready.", border_style="bright_green"
            ))
            time.sleep(1)

    except Exception as e:
        console.print(f"[red]Error in welcome screen: {e}[/]")
        sys.exit(1)


# ------------------------------------------------------------------------------
# Script Runner
# ------------------------------------------------------------------------------
def run_script(script_name):
    """Fetch and run a script from your GitHub repo"""
    token = GITHUB_TOKEN
    headers_str = f"Authorization: token {token}"

    try:
        # Binary executable (no extension)
        if not script_name.endswith(".sh") and not script_name.endswith(".py"):
            temp_dir = "/data/data/com.termux/files/usr/tmp/astitva_temp"
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, script_name)
            try:
                file_content = get_file_from_github(script_name)
                with open(temp_path, "wb") as f:
                    f.write(file_content)
                os.chmod(temp_path, 0o755)
                console.print(f":rocket: [bold green]Executing {script_name}...[/]")
                subprocess.run([temp_path], check=True)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            return

        # Shell script
        if script_name.endswith(".sh"):
            console.print(f":terminal: [bold]Executing: {script_name}[/]")
            raw_url = (
                f"https://raw.githubusercontent.com/{GITHUB_USERNAME}"
                f"/{GITHUB_REPO}/{GITHUB_BRANCH}/{script_name}"
            )
            subprocess.run([
                "bash", "-c",
                f"curl -H '{headers_str}' -s '{raw_url}' | tr -d '\\r' | bash"
            ], check=True)
            return

        # Python script
        console.print(f":snake: [bold]Executing: {script_name}[/]")
        subprocess.run([
            "python", "-c",
            f"import requests, base64; "
            f"r = requests.get("
            f"  'https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}"
            f"/contents/{script_name}',"
            f"  headers={{'Authorization': 'token {token}'}}); "
            f"exec(base64.b64decode(r.json()['content']).decode())"
        ], check=True)

    except subprocess.CalledProcessError as e:
        sanitized = str(e).replace(token, "****")
        console.print(f":x: [bright_red]Script execution failed: {sanitized}[/]")
    except Exception as e:
        sanitized = str(e).replace(token, "****")
        console.print(f":x: [bright_red]Unexpected error: {sanitized}[/]")
    finally:
        input("EXITING✋: Press Enter to return to main menu...")
        os.system("clear")


# ------------------------------------------------------------------------------
# Shared Menu Helpers
# ------------------------------------------------------------------------------
def _build_panels(options):
    panels = []
    for idx, (key, label, script, emoji) in enumerate(options):
        border_color, text_color = COLOR_SCHEME[idx % len(COLOR_SCHEME)]
        content = Text.assemble(
            (f"{key}. ",  f"bold {text_color}"),
            (emoji,       f"bold italic {text_color}"),
            (f" {label}", f"bold {text_color}")
        )
        panels.append(Panel(content, border_style=border_color, padding=(1, 2), style="none"))
    return panels


def _run_menu(banner_text, menu_title, subtitle, panel_title, options):
    while True:
        os.system("clear")
        os.system(f'toilet -f smblock --gay "{banner_text}"')
        console.print(Panel(
            Text(menu_title, style="bold white on purple"),
            subtitle=subtitle,
            border_style="bright_magenta"
        ))
        option_panels = _build_panels(options)
        console.print(Panel(
            Columns(option_panels, equal=True, expand=True),
            title=f":control_knobs: {panel_title}",
            border_style="bright_red"
        ))

        choice = Prompt.ask(":arrow_forward: Enter your choice", default="X").strip().upper()
        if choice == "X":
            return

        try:
            selected = next(item for item in options if item[0] == choice)
            script_name = selected[2]
            if script_name:
                run_script(script_name)
            else:
                console.print("[red]No script assigned to this option.[/]")
                time.sleep(1)
        except StopIteration:
            console.print("[red]Invalid selection. Try again.[/]")
            time.sleep(1)


# ------------------------------------------------------------------------------
# OBB MODE
# ------------------------------------------------------------------------------
def obb_menu():
    _run_menu(
        "OBB MODE", "OBB MODE MENU", ":cd: OBB Features", "OBB Menu",
        [
            ("1", "AUTO REPACK",        "repack.sh",     "🔄"),
            ("2", "MOD GUN ALL IN ONE", "mod_gun.py",    "🔫"),
            ("3", "MOD ALL SKIN",       "mod_skin.py",   "👕"),
            ("4", "EMOTE OBB",          "emote.py",      "🐒"),
            ("5", "MOD LOBBY",          "mod_lobby.py",  "🎮"),
            ("6", "SIZE FIX GUN",       "sizfixgun.py",  "🔧"),
            ("7", "SIZE FIX SKIN",      "sizefixskin.py","🔥"),
            ("X", "Go Back",            None,            "↩️"),
        ]
    )


# ------------------------------------------------------------------------------
# PAK MODE
# ------------------------------------------------------------------------------
def pak_menu():
    _run_menu(
        "PAK MODE", "PAK MODE MENU", ":package: PAK Features", "PAK Menu",
        [
            ("1", "MOD HIT EFF PAK",   "hit_effect.py",      "💥"),
            ("2", "MOD KILL MESSAGE",  "mod_killmessage.py",  "🎯"),
            ("3", "ENTRY EMOTE",       "entry.py",            "💌"),
            ("4", "PAK UNPACK REPACK", "pak.py",              "💕"),
            ("5", "SKIN PAK",          "skinpak.py",          "🎮"),
            ("6", "LOOTBOX PAK",       "lootboxpak.py",       "🎮"),
            ("X", "Go Back",           None,                  "↩️"),
        ]
    )


# ------------------------------------------------------------------------------
# EXTRA FEATURES
# ------------------------------------------------------------------------------
def extra_menu():
    extra_options = [
        ("1", "ID, HEX, NAME",        "idnm.py",        "💥"),
        ("2", "INDEX FINDER",          "indexfinder.py", "🔎"),
        ("3", "HEX AND STRING SEARCH", "srch.py",        "🔎"),
        ("4", "ABOUT TOOL",            None,             "💲"),
        ("5", "ICON DAT FINDER",       "icondat.py",     "🔎"),
        ("X", "Go Back",               None,             "↩️"),
    ]

    while True:
        os.system("clear")
        os.system('toilet -f smblock --gay "EXTRA"')
        console.print(Panel(
            Text("EXTRA FEATURES MENU", style="bold white on purple"),
            subtitle=":rocket: Additional Tools",
            border_style="bright_magenta"
        ))
        option_panels = _build_panels(extra_options)
        console.print(Panel(
            Columns(option_panels, equal=True, expand=True),
            title=":control_knobs: Extra Features",
            border_style="bright_red"
        ))

        choice = Prompt.ask(":arrow_forward: Enter your choice", default="X").strip().upper()
        if choice == "X":
            return

        try:
            selected = next(item for item in extra_options if item[0] == choice)

            if selected[1] == "ABOUT TOOL":
                console.print(Panel(
                    Text(
                        "ASTITVA MODDING TOOL\n"
                        "Version  : 4.3\n"
                        "Made by  : Astitva\n"
                        "Security : Open (No Verification)",
                        style="bold white on purple"
                    ),
                    subtitle=":tools: About",
                    border_style="bright_magenta"
                ))
                input("Press Enter to return to menu...")
            elif selected[2]:
                run_script(selected[2])
            else:
                console.print("[red]No sc
