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
            botpassword = os.getenv("irc_pass")
            if None not in (channel, botnick, botpassword):
                self.send_report_to_itc(
                    server, port, channel, botnick, botpassword
                )
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
        botpassword: str,
    ) -> None:
        """
        Send the update report to IRC chat.
        """
        irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_context = ssl.create_default_context()
        irc = ssl_context.wrap_socket(irc, server_hostname=server)

        irc.connect((server, port))

        # Send the necessary commands to identify the bot and join the channel
        irc.send(
            bytes(
                "USER "
                + botnick
                + " "
                + botnick
                + " "
                + botnick
                + " "
                + botnick
                + "\n",
                "UTF-8",
            )
        )
        irc.send(bytes("NICK " + botnick + "\n", "UTF-8"))
        irc.send(
            bytes(
                "PRIVMSG NickServ :IDENTIFY "
                + botnick
                + " "
                + botpassword
                + "\n",
                "UTF-8",
            )
        )
        time.sleep(10)

        irc.send(bytes("JOIN " + channel + "\n", "UTF-8"))

        message = "I AM CROCUBOT"
        irc.send(bytes("PRIVMSG " + channel + " :" + message + "\n", "UTF-8"))

        time.sleep(30)

        irc.send(bytes("QUIT \n", "UTF-8"))
        irc.close()


if __name__ == "__main__":
    notify = Notifier(notification_type="irc", report={})
