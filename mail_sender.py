import email.utils
import logging
import smtplib
from datetime import timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class MailSender:

    def __init__(self, mailconfig: dict, log: logging.Logger):
        self.mailconfig = mailconfig
        self.log = log

    def send_finish_info(self, printer: str, file: str, print_time: int) -> None:
        """
        Sends a mail to the recipient specified in the config.json file

        """
        msg = MIMEMultipart()
        msg['From'] = self.mailconfig['sender']
        msg['To'] = self.mailconfig['recipient']
        msg['Subject'] = 'Print finished: ' + file
        msg['Message-ID'] = email.utils.make_msgid()
        body = 'Print ' + file + " finished on " + printer + " (print time: " + str(timedelta(seconds=print_time)) + ")."
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(self.mailconfig['host'], self.mailconfig['port'])
        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(self.mailconfig['user'], self.mailconfig['password'])

        server.sendmail(self.mailconfig['sender'], self.mailconfig['recipient'], msg.as_string())
