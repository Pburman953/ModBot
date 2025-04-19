
from backend import config
import socket


def ban_user(irc_socket, channel, username, message):
    """
    Bans a user from the Twitch channel.
    """
    irc_socket.send(f"PRIVMSG #{channel} :/ban {username}\r\n".encode("utf-8"))

    irc_socket.send(f"PRIVMSG {config.CHANNEL} :{message}\n".encode("utf-8"))

    print(f"[ModBot] Banned {username}.") 