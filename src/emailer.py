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

    if plaintext:
        part1 = MIMEText(plaintext, 'plain', 'utf-8')
        msg.attach(part1)

    if html:
        part2 = MIMEText(html, 'html', 'utf-8')
        msg.attach(part2)

    # See http://stackoverflow.com/a/17115349/1222351 for MIME structure
    outer = MIMEMultipart('mixed')
    outer['Subject'] = subject
    outer['From'] = config['email_from']
    outer['To'] = to_address
    outer['Message-Id'] = make_msgid()
    outer.attach(msg)
    attach_files(outer, files)
    _send(outer)

def attach_files(msg, files):
    for f in files:
        with open(f, 'rb') as fil:
            filename = os.path.basename(fil.name)
            attachment = MIMEApplication(fil.read(), _subtype=os.path.splitext(filename)[1][1:])
            attachment.add_header('Content-Disposition', 'attachment',
                    filename=filename)
            msg.attach(attachment)

# Authenticates, then actually sends the message
def _send(msg):
    s = smtplib.SMTP(config['smtp_host'], int(config['smtp_port']))
    s.starttls()
    if 'email_username' in config and 'email_password' in config:
        s.login(config['email_username'], config['email_password'])
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()

# Testing
if __name__ == "__main__":
    send_plaintext(
        'bearbot.61b@gmail.com',
        '[cs61b] Plaintext!',
        'This is the plaintext version. Can you see this?')
    print "Sent plaintext."

    send_html(
        'bearbot.61b@gmail.com',
        '[cs61b] HTML?',
        '<b>This is the html version</b>. Can you see this?')
    print "Sent HTML."

    send_template(
        'bearbot.61b@gmail.com',
        '[cs61b] Template.',
        'registered.html',
        files=['account_forms/test.pdf'],
        user={'email': 'bearbot.61b@gmail.com', 'github': 'rimslorka'})
    print "Sent template."

    send_markdown(
        'bearbot.61b@gmail.com',
        '[cs61b] Markdown!',
        '*This is the html version*. <b>Were the gats escaped?</b>',
        ['LICENSE', 'README.md'])
    print "Sent Markdown."
