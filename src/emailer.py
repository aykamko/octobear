import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, PackageLoader
from . import config

def send_plaintext(to_address, subject, plaintext):
    # TODO: @austin
    pass

def send_html(to_address, subject, html_string):
    # TODO: @austin
    pass

def send_template(to_address, subject, template_name, **kwargs):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = config['email_from']
    msg['To'] = to_address

    # Create the body of the message (a plain-text and an HTML version).
    text = "HTML failed to render =(.\nPlease let us know about this!"

    # Render the HTML version
    env = Environment(loader=PackageLoader('src'))
    template = env.get_template(template_name)
    html = template.render(kwargs)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Credentials (if needed)
    username = config['email_username']
    password = config['email_password']

    # The actual mail send
    s = smtplib.SMTP(config['smtp_host'], int(config['smtp_port']))
    s.starttls()
    s.login(username,password)
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()
