import smtplib
import markdown2

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, PackageLoader
from . import config

# Creates and emails a text/plain message
def send_plaintext(to_address, subject, plaintext):
    msg = MIMEText(plaintext)
    msg['Subject'] = subject
    msg['From'] = config['email_from']
    msg['To'] = to_address
    _send(msg)

# Creates and emails an HTML message, with a backup plaintext message
def send_html(to_address, subject, html_string):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = config['email_from']
    msg['To'] = to_address

    # Create the body of the message (a plain-text and an HTML version).
    text = "HTML failed to render =(.\nPlease let us know about this!"

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html_string, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    _send(msg)

# Renders the specified template to HTML, then emails it
def send_template(to_address, subject, template_name, **kwargs):
    env = Environment(loader=PackageLoader('src'))
    template = env.get_template(template_name)
    html = template.render(kwargs)

    send_html(to_address, subject, html)

# Renders the given markdown to HTML, then emails it
def send_markdown(to_address, subject, markdown):
    html = markdown2.markdown(markdown, safe_mode='escape')
    send_html(to_address, subject, html)

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
