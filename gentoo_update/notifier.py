import os
import socket
import ssl
import time
from sys import exit
from typing import List, Tuple

USE_SENDGRID = True
try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content
except ImportError:
    USE_SENDGRID = False


class Notifier:
    def __init__(
        self, notification_type: str, report: List, short=True
    ) -> None:
        report = report[0:2] if short else report

        if notification_type == "email":
            if USE_SENDGRID:
                self.send_report_to_mail(report)
            else:
                print("sendgrid library is not installed")
                print("it can be installed from GURU overlay:")
                print("  emerge --ask dev-python/sendgrid")
        elif notification_type == "irc":
            self.send_report_to_irc(report)
        else:
            print("Unsupported authentication methods")
            print("Currently supporting: irc")
            print("Exiting...")

    def get_irc_vars(self) -> Tuple[str, str, str]:
        """
        Get variables needed to send report to IRC chat from env.
        """
        channel = os.getenv("IRC_CHANNEL")
        botnick = os.getenv("IRC_BOT_NICKNAME")
        botpass = os.getenv("IRC_BOT_PASSWORD")
        if None not in (channel, botnick, botpass):
            return channel, botnick, botpass
        else:
            print("Undefined enviromental variable(s)")
            print(
                "Please define: IRC_CHANNEL, IRC_BOT_NICKNAME, IRC_BOT_PASSWORD"
            )
            exit(1)

    def send_report_to_irc(self, report: List[str]) -> None:
        """
        Send the update report to IRC chat.
        """
        server = "irc.libera.chat"
        port = 6697
        channel, botnick, botpass = self.get_irc_vars()
        ssl_context = ssl.create_default_context()

        irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        irc = ssl_context.wrap_socket(irc, server_hostname=server)
        irc.connect((server, port))
        irc.send(
            f"USER {botnick} {botnick} {botnick} {botnick}\n".encode("UTF-8")
        )
        irc.send(f"NICK {botnick}\n".encode("UTF-8"))
        irc.send(
            f"PRIVMSG NickServ :IDENTIFY {botnick} {botpass}\n".encode("UTF-8")
        )
        time.sleep(5)

        irc.send(f"JOIN {channel}\n".encode("UTF-8"))
        for line in report:
            irc.send(f"PRIVMSG {channel} :{line}\n".encode("UTF-8"))
            time.sleep(10)
        print("report sent, quitting...")

        irc.send("QUIT \n".encode("UTF-8"))
        irc.close()

    def get_mail_vars(self) -> Tuple[str, str, str]:
        """
        Get variables needed to send report to email via SendGrid from env.
        """
        api_key = os.getenv("SENDGRID_API_KEY")
        send_to = os.getenv("SENDGRID_TO")
        send_from = os.getenv("SENDGRID_FROM")
        if None not in (api_key, send_to, send_from):
            return api_key, send_to, send_from
        else:
            print("Undefined enviromental variable(s)")
            print("Please define: SENDGRID_API_KEY, SENDGRID_TO, SENDGRID_FROM")
            exit(1)

    def send_report_to_mail(self, report: List[str]) -> None:
        """
        Send the update report to email via SendGrid.
        """
        api_key, send_to, send_from = self.get_mail_vars()
        sendgrid_client = sendgrid.SendGridAPIClient(api_key=api_key)
        subject = "Gentoo Linux Update Report"

        content = Content("text/plain", "\n".join(report))
        mail = Mail(Email(send_from), To(send_to), subject, content)
        mail_json = mail.get()

        response = sendgrid_client.client.mail.send.post(request_body=mail_json)
        if response.status_code == 202:
            print("email was sent successfully!")
        else:
            print("email was not sent successfully, details:")
            print(response)


if __name__ == "__main__":
    report = [
        "==========> Gentoo Update Report <==========",
        "update status: SUCCESS",
        "processed packages:",
        "--- sys-apps/sandbox 2.32->2.37",
        "",
        "Disk Usage Stats:",
        "Free Space 35G => 35G",
        "Used Space 7.5G => 7.5G",
        "Used pc(%) 18% => 18%",
    ]
    notify = Notifier(notification_type="email", report=report, short=False)
