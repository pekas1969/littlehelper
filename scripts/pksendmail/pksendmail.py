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
import smtplib
import argparse
import configparser
from email.message import EmailMessage
from email.utils import formataddr
from mimetypes import guess_type
from pathlib import Path

def load_config(account_name):
    config_path = os.path.expanduser(f'~/.config/pksendmail/{account_name}.conf')
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    config = configparser.ConfigParser()
    config.read(config_path)
    if 'account' not in config:
        raise KeyError(f"Missing [account] section in {config_path}")
    return config['account']

def create_email(cfg, to_address, subject, message, attachment_path=None):
    msg = EmailMessage()
    msg['From'] = formataddr((cfg.get('name', ''), cfg['auth_user']))
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.set_content(message)

    if attachment_path:
        file_path = Path(attachment_path)
        if not file_path.is_file():
            raise FileNotFoundError(f"Attachment not found: {attachment_path}")

        mime_type, _ = guess_type(file_path)
        mime_type = mime_type or 'application/octet-stream'
        maintype, subtype = mime_type.split('/', 1)

        with file_path.open('rb') as f:
            data = f.read()
            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=file_path.name)
        print(f"✓ Attachment '{file_path.name}' added to email.")

    return msg

def send_mail(cfg, msg):
    smtp_server = cfg.get('server')
    smtp_port = int(cfg.get('port', 587))
    auth_method = cfg.get('auth_method', 'starttls').lower()

    print(f"→ Connecting to {smtp_server}:{smtp_port} using method: {auth_method}")

    if auth_method in ['starttls', 'tls']:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.set_debuglevel(1)  # show communication
        server.ehlo()
        server.starttls()
        server.ehlo()
    elif auth_method == 'ssl':
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.set_debuglevel(1)
    elif auth_method == 'none':
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.set_debuglevel(1)
    else:
        raise ValueError(f"Unsupported auth_method: {auth_method}")

    print("→ Logging in...")
    server.login(cfg['auth_user'], cfg['auth_password'])
    print("✓ Login successful.")

    print("→ Sending email...")
    server.send_message(msg)
    print("✓ Email sent.")
    server.quit()

def main():
    parser = argparse.ArgumentParser(description='Versendet E-Mails über SMTP per Terminal')
    parser.add_argument('--from', dest='from_account', required=True, help='Name der Account-Config (z. B. pkasparak_gmail)')
    parser.add_argument('--to', required=True, help='Empfängeradresse')
    parser.add_argument('--subject', required=True, help='Betreff der E-Mail')
    parser.add_argument('--message', required=True, help='Inhalt der E-Mail')
    parser.add_argument('--file', dest='attachment', help='Pfad zu einem Anhang (optional)')
    args = parser.parse_args()

    try:
        cfg = load_config(args.from_account)
        email_msg = create_email(cfg, args.to, args.subject, args.message, args.attachment)
        send_mail(cfg, email_msg)
    except Exception as e:
        print(f"✗ Fehler: {e}")

if __name__ == '__main__':
    main()
