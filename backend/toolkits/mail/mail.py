from email.mime.multipart import MIMEMultipart
from apps.config.schema import MailSchema
from email.mime.text import MIMEText
from config import settings
from typing import List
import logging.config
import logging
import smtplib
import ssl

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")


class MailToolkit:
    def __init__(self, test_mail_schema: MailSchema):
        self.auth: bool = test_mail_schema.auth
        self.email: str = test_mail_schema.email
        self.password: str = test_mail_schema.password
        self.ssl: bool = test_mail_schema.ssl
        self.smtp_server: str = test_mail_schema.smtp_server
        self.smtp_port: int = test_mail_schema.smtp_port

    def authenticate(self):
        service = smtplib.SMTP(
            self.smtp_server,
            self.smtp_port
        )
        if self.ssl:
            service.starttls()

        service.set_debuglevel(settings.DEBUG)
        service.login(self.email, self.password)
        return service
        

    def get_service(self):
        service = smtplib.SMTP(self.smtp_server, self.smtp_port)
        service.set_debuglevel(settings.DEBUG)
        service.ehlo()
        return service

    def send(self, to: List[str], subject, body):
        try:
            if self.auth:
                service = self.authenticate()
            else:
                service = self.get_service()
            
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = ",".join(to)
            msg['Subject'] = subject

            msg.attach(MIMEText(body, "html"))

            service.sendmail(
                self.email,
                to,
                msg.as_string()
            )

            service.quit()
        except Exception as e:
            logger.critical(e, exc_info=1)
            raise

