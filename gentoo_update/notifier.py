import os
import socket
import ssl
import time
from sys import exit
from typing import List, Tuple


class Notifier:
    def __init__(self, notification_type: str, report: List, short=True) -> None:
        if notification_type == "email":
            pass
        elif notification_type == "irc":
            server = "irc.libera.chat"
            port = 6697
            channel, botnick, botpass = self.get_irc_vars()
            report = report[0:2] if short else report
            self.send_report_to_irc(report, server, port, channel, botnick, botpass)
        else:
            print("Unsupported authentication methods")
            print("Currently supporting: irc")
            print("Exiting...")

    def get_irc_vars(self) -> Tuple[str, str, str]:
        """
        Get variables needed to send report to IRC chat from env.
        """
        channel = os.getenv("irc_chan")
        botnick = os.getenv("irc_nick")
        botpass = os.getenv("irc_pass")
        if None not in (channel, botnick, botpass):
            return channel, botnick, botpass
        else:
            print("Undefined enviromental variable(s)")
            print("Please define: irc_chan, irc_nick and irc_pass variables")
            exit(1)

    def send_report_to_irc(
        self,
        report: List,
        server: str,
        port: int,
        channel: str,
        botnick: str,
        botpass: str,
    ) -> None:
        """
        Send the update report to IRC chat.
        """
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
        time.sleep(10)

        irc.send(f"JOIN {channel}\n".encode("UTF-8"))
        for line in report:
            irc.send(f"PRIVMSG {channel} :{line}\n".encode("UTF-8"))
            time.sleep(15)
        print("report sent, quitting...")

        irc.send("QUIT \n".encode("UTF-8"))
        irc.close()


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
        "Used pc(%) 18% => 18%"
    ]
    notify = Notifier(notification_type="irc", report=report)
