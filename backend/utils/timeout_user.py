from backend import config
import socket


def timeout_user(irc_socket, channel, username, duration, message):
    """
    Timeouts a user for a specified duration (default 600s = 10 mins).
    """
    irc_socket.send(f"PRIVMSG #{channel} :/timeout {username} {duration}\r\n".encode("utf-8"))

    print(f"[ModBot] Timed out {username} for {duration} seconds. {message}")