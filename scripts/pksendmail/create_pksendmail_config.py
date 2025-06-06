#version 0.0.1

#============================================================================
#MIT License
#
#Copyright (c) 2025 Peter Kasparak <peter.kasparak@gmail.com>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#DEALINGS IN THE SOFTWARE.
#============================================================================

#!/usr/bin/env python3
import os
from pathlib import Path
import configparser

def ask(prompt, default=None, required=True):
    while True:
        val = input(f"{prompt}{' [' + default + ']' if default else ''}: ").strip()
        if val:
            return val
        elif default is not None:
            return default
        elif not required:
            return ""
        else:
            print("This field is required.")

def main():
    print("=== Create new pksendmail config ===")
    name = ask("Config name (without or with .conf)")
    if not name.endswith(".conf"):
        name += ".conf"

    config_dir = Path.home() / ".config" / "pksendmail"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / name

    print(f"\nCreating: {config_path}")

    full_name = ask("Your full name")
    smtp_server = ask("SMTP server", "smtp.gmail.com")
    port = ask("SMTP port", "587")
    email = ask("Your email address (auth_user)")
    auth_method = ask("Auth method (ssl, tls, starttls)", "starttls")
    password = ask("Password (leave empty to enter later)", required=False)

    config = configparser.ConfigParser()
    config["account"] = {
        "name": full_name,
        "server": smtp_server,
        "port": port,
        "auth_user": email,
        "auth_method": auth_method
    }
    if password:
        config["account"]["auth_password"] = password

    with open(config_path, "w") as f:
        config.write(f)

    print(f"\n✓ Config saved to: {config_path}")

if __name__ == "__main__":
    main()
