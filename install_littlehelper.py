#!/usr/bin/env python3

import os
import sys
import requests
import shutil
import yaml
import re
from termcolor import colored

REPO_BASE = "https://raw.githubusercontent.com/pekas1969/littlehelper/main"
YAML_URL = f"{REPO_BASE}/scripts.yaml"
LOCAL_DIRS = ["/usr/local/bin", os.path.expanduser("~/.local/bin")]

def fetch_yaml():
    try:
        resp = requests.get(YAML_URL)
        resp.raise_for_status()
        return yaml.safe_load(resp.text)
    except Exception as e:
        print(f"Failed to fetch scripts.yaml: {e}")
        sys.exit(1)

def get_installed_version(path):
    try:
        with open(path, "r") as f:
            for line in f:
                match = re.match(r"#\s*version\s*=\s*(\S+)", line.strip())
                if match:
                    return match.group(1)
    except:
        pass
    return None

def get_install_status(script_name):
    for path in LOCAL_DIRS:
        full = os.path.join(path, script_name)
        if os.path.exists(full):
            return full, get_installed_version(full)
    return None, None

def compare_versions(v1, v2):
    def normalize(v):
        return [int(x) if x.isdigit() else x for x in re.split(r'[.-]', v)]
    return normalize(v1) < normalize(v2)

def script_url(script_name):
    subdir = script_name.split(".")[0]  # e.g., pkmangui.py → pkmangui
    return f"{REPO_BASE}/scripts/{subdir}/{script_name}"

def show_menu(scripts):
    actions = []
    print("Available scripts:")
    print("------------------")

    for idx, entry in enumerate(scripts, 1):
        name = entry["name"]
        desc = entry.get("description", "")
        version = entry.get("version", "0.0.0")
        installed_path, installed_version = get_install_status(name)

        if installed_path:
            if installed_version and compare_versions(installed_version, version):
                label = f"{idx} - Update or uninstall {colored(name, 'blue')} (installed: {installed_version} in {installed_path})"
                actions.append(("update_or_uninstall", entry, installed_path))
            else:
                label = f"{idx} - Uninstall {colored(name, 'blue')} (installed: {installed_version} in {installed_path})"
                actions.append(("uninstall", entry, installed_path))
        else:
            label = f"{idx} - Install {colored(name, 'green')} ({desc})"
            actions.append(("install", entry, None))
        print(label)

    print(" Q|q - Quit")
    return actions

def download_and_install(script_name, target):
    url = script_url(script_name)
    try:
        response = requests.get(url)
        response.raise_for_status()
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w") as f:
            f.write(response.text)
        os.chmod(target, 0o755)
        print(f"{script_name} installed to {target}")
    except Exception as e:
        print(f"Failed to install {script_name}: {e}")

def uninstall_script(path):
    try:
        os.remove(path)
        print(f"Removed {path}")
    except Exception as e:
        print(f"Failed to remove {path}: {e}")

def main():
    scripts = fetch_yaml().get("scripts", [])
    while True:
        actions = show_menu(scripts)
        choice = input("Choose a script to act on or [Q]: ").strip()
        if choice.lower() == 'q':
            print("Goodbye.")
            break

        if not choice.isdigit() or not (1 <= int(choice) <= len(actions)):
            print("Invalid choice. Try again.")
            continue

        action, entry, path = actions[int(choice) - 1]
        name = entry["name"]
        version = entry.get("version", "0.0.0")

        if action == "install":
            scope = input("Install for user (u) or globally (g)? [u/g]: ").strip().lower()
            if scope == 'g':
                target = f"/usr/local/bin/{name}"
                if os.geteuid() != 0:
                    print("Need sudo to install globally.")
                    os.system(f"sudo curl -s {script_url(name)} -o {target} && sudo chmod +x {target}")
                else:
                    download_and_install(name, target)
            else:
                target = os.path.expanduser(f"~/.local/bin/{name}")
                download_and_install(name, target)

        elif action in ("uninstall", "update_or_uninstall"):
            if action == "update_or_uninstall":
                print(f"1 - Update {name}")
                print(f"2 - Uninstall {name}")
                sub = input("Choose action: ").strip()
                if sub == "1":
                    download_and_install(name, path)
                elif sub == "2":
                    uninstall_script(path)
            else:
                confirm = input(f"Really uninstall {name}? [y/N]: ").strip().lower()
                if confirm == "y":
                    uninstall_script(path)

        input("Press Enter to continue...")

if __name__ == "__main__":
    main()
