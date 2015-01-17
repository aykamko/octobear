import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, PackageLoader

def send_plaintext(to_address, subject, plaintext):
    # TODO: @austin
    pass

def send_markdown(to_address, subject, html_string):
    # TODO: @austin
    pass

def send(user, subject, template):
    # me == my email address
    # you == recipient's email address
    me = "cs61b@sandboxe9b32d5651b3403c820ae7c5d2cd3926.mailgun.org"
    you = user[u'email']

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = you

    # Create the body of the message (a plain-text and an HTML version).
    text = "HTML failed to render =(.\nPlease let us know about this!"

    # Render the HTML version
    env = Environment(loader=PackageLoader('src'))
    template = env.get_template(template)
    html = template.render(user=user)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Credentials (if needed)
    username = 'postmaster@sandboxe9b32d5651b3403c820ae7c5d2cd3926.mailgun.org'
    password = 'e581750b7b1dfe506b85398c747c6fc6'

    # The actual mail send
    s = smtplib.SMTP('smtp.mailgun.org', 587)
    s.starttls()
    s.login(username,password)
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(me, you, msg.as_string())
    s.quit()
