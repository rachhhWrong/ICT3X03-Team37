from flask_mail import Mail
from os import environ as env

mail = None

# sanitize input by allowing only alphanumerics
MAILSERVER = env.get("MAIL_SERVER", 'smtp.gmail.com')
MAILPORT = int(env.get("MAIL_PORT", "465"))
SENDER_ADDR = env.get("MAIL_USERNAME", None)
SENDER_PASS = env.get("MAIL_PASSWORD", None)

if SENDER_ADDR is None:
    raise EnvironmentError("Email Username Not Set in environment variables!")
if SENDER_PASS is None:
    raise EnvironmentError("Email Password Not Set in environment variables!")

def start_mail(app):
    app.config['MAIL_SERVER'] = MAILSERVER
    app.config['MAIL_PORT'] = MAILPORT
    app.config['MAIL_USERNAME'] = SENDER_ADDR
    app.config['MAIL_PASSWORD'] = SENDER_PASS
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    global mail
    mail = Mail(app)
    return mail
