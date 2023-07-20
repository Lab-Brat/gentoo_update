import os
import socket
import ssl
import time
from typing import Dict


class Notifier:
    def __init__(self, notification_type: str, report: Dict) -> None:
        if notification_type == "email":
            pass
        elif notification_type == "irc":
            server = "irc.libera.chat"
            port = 6697
            channel = os.getenv("irc_chan")
            botnick = os.getenv("irc_nick")
            botpass = os.getenv("irc_pass")
            if None not in (channel, botnick, botpass):
                self.send_report_to_itc(server, port, channel, botnick, botpass)
            else:
                print("Undefined enviromental variable(s)")
                print(
                    "Please define: irc_chan, irc_nick and irc_pass variables"
                )
        else:
            print("Unsupported authentication methods")
            print("Currently supporting: irc")
            print("Exiting...")

    def send_report_to_itc(
        self,
        server: str,
        port: int,
        channel: str,
        botnick: str,
        botpass: str,
    ) -> None:
        """
        Send the update report to IRC chat.
        """
        message = "I AM CROCUBOT"
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
        irc.send(f"PRIVMSG {channel} :{message}\n".encode("UTF-8"))
        time.sleep(20)

        irc.send("QUIT \n".encode("UTF-8"))
        irc.close()


if __name__ == "__main__":
    notify = Notifier(notification_type="irc", report={})
