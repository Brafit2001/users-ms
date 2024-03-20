import smtplib
import ssl
import string
import traceback
from email.message import EmailMessage
from email.utils import formataddr
from http import HTTPStatus

from decouple import config
from flask import render_template, jsonify

from api.utils.Logger import Logger


def sendPasswordEmail(user, subject, template):
    try:
        email_sender = 'clipclassuc3m@gmail.com'
        credential = config('GOOGLE_PASSWORD')
        email_receiver = user.email

        # Email template and vars
        body = render_template(template)
        body = string.Template(body).substitute(name=user.name, surname=user.surname, username=user.surname,
                                                password=user.password)

        # Build email
        em = EmailMessage()
        em['From'] = formataddr(('Clipclass Platform', email_sender))
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body, subtype="html")

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.ehlo()
            smtp.login(email_sender, credential)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
            smtp.close()
        return True
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        return False
