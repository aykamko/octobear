import smtplib
import markdown2
import os

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
from jinja2 import Environment, PackageLoader
from . import config

# Creates and emails a text/plain message
def send_plaintext(to_address, subject, plaintext, files=[]):
    send_mixed(to_address, subject, plaintext=plaintext, files=files)

# Creates and emails an HTML message
def send_html(to_address, subject, html, files=[]):
    send_mixed(to_address, subject, html=html, files=files)

# Renders the specified template to HTML, then emails it
def send_template(to_address, subject, template_name, files=[], **kwargs):
    env = Environment(loader=PackageLoader('src'))
    template = env.get_template(template_name)
    html = template.render(kwargs)

    send_html(to_address, subject, html, files)

# Renders the given markdown to HTML, then emails it
def send_markdown(to_address, subject, markdown, files=[]):
    html = markdown2.markdown(markdown, safe_mode='escape')
    send_mixed(to_address, subject, plaintext=markdown, html=html, files=files)

# Creates and emails an HTML/plaintext mixed message
def send_mixed(to_address, subject, plaintext=None, html=None, files=[]):

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = config['email_from']
    msg['To'] = to_address
    msg['Message-Id'] = make_msgid()

    if plaintext:
        part1 = MIMEText(plaintext, 'plain')
        msg.attach(part1)

    if html:
        part2 = MIMEText(html, 'html')
        msg.attach(part2)

    attach_files(msg, files)

    _send(msg)

def attach_files(msg, files):
    for f in files:
        with open(f, 'rb') as fil:
            filename = os.path.basename(fil.name)
            attachment = MIMEApplication(fil.read(), _subtype=os.path.splitext(filename)[1][1:])
            attachment.add_header('content-disposition', 'attachment',
                    filename=('utf-8', '', filename))
            msg.attach(attachment)

# Authenticates, then actually sends the message
def _send(msg):
    s = smtplib.SMTP(config['smtp_host'], int(config['smtp_port']))
    s.starttls()
    s.login(config['email_username'], config['email_password'])
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()

# Testing
if __name__ == "__main__":
    send_plaintext(
        'akrolsmir@gmail.com',
        '[cs61b] Plaintext!',
        'This is the plaintext version. Can you see this?')

    send_html(
        'akrolsmir@gmail.com',
        '[cs61b] HTML?',
        '<b>This is the html version</b>. Can you see this?')

    send_template(
        'akrolsmir@gmail.com',
        '[cs61b] Template.',
        'registered.html',
        user={'email': 'akrolsmir@gmail.com', 'github': 'rimslorka'})

    send_markdown(
        'akrolsmir@gmail.com',
        '[cs61b] Markdown!',
        '*This is the html version*. <b>Were the gats escaped?</b>')
