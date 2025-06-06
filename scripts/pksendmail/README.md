# pksendmail

**pksendmail** is a lightweight Python-based console tool for sending emails using SMTP via predefined configuration files. It supports multiple accounts and optional file attachments. A companion script is included to easily create account configuration files.

## Features

- Send emails via console using a simple command-line interface
- Supports multiple email accounts via per-account config files
- TLS and STARTTLS support
- Optional file attachments
- Passwords are requested securely at runtime (not stored in plain text)
- Clean and verbose logging of SMTP interactions
- Helper script for creating new account configs interactively

---

## Requirements

- Python 3.7+
- No external dependencies (uses standard library)

---

## Installation

1. Download the projectfiles pksendmail.py and create_pksendmail_config.py from: https://github.com/pekas1969/littlehelper/tree/main/scripts/pksendmail

2. (Optional) Make scripts executable:
   ```bash
   chmod +x pksendmail.py create_pksendmail_config.py
   ```

---

## Usage

### 1. Create a new account config

Use the helper script to create a new email account configuration file:

```bash
python3 create_pksendmail_config.py
```

You will be prompted to enter:

- Config name (e.g. `my_gmail.conf`)
- Full name (sender's name)
- SMTP server address
- Port
- Email address (SMTP login)
- Authentication method (`tls`, `starttls`, or `plain`)

The config will be saved to:

```bash
~/.config/pksendmail/<your-config>.conf
```

⚠️ **Passwords are NOT stored in the config file.** You will be prompted for your password at runtime when sending mail.
You can add a line

```bash
auth_password = your password here
```

but it's stored in plain format!

---

### 2. Send an email

```bash
python3 pksendmail.py \
  --from <config_name_without_.conf> \
  --to <recipient_email> \
  --subject "Subject Line" \
  --message "Body of the email" \
  [--file /path/to/attachment]
```

#### Example

```bash
python3 pksendmail.py \
  --from my_gmail \
  --to friend@example.com \
  --subject "Greetings from Terminal" \
  --message "This is a test email from the command line."
```

Optional attachment:
```bash
  --file ./myfile.pdf
```

---

## Config File Format

Each config file is stored under:

```bash
~/.config/pksendmail/
```

Example: `pkasparak_gmail.conf`

```ini
[account]
name = Peter Kasparak
server = smtp.gmail.com
port = 587
auth_user = pkasparak@gmail.com
auth_method = tls
```

Valid values for `auth_method`:
- `tls` (default for port 587)
- `starttls`
- `plain` (unencrypted, only use on trusted networks)

⚠️ Do **not** include `auth_password` in the config. It will be securely prompted during execution.

---

## Security Notes

- Passwords are entered at runtime using `getpass` (input hidden).
- No passwords are saved on disk.
- Use App Passwords for providers like Gmail if 2FA is enabled.

---

## License

MIT License

---

## Author

Peter Kasparak <peter.pasparak@gmail.com>
