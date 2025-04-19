
def timeout_user(irc_socket, channel, username, duration):
    """
    Timeouts a user for a specified duration (default 600s = 10 mins).
    """
    command = f"PRIVMSG #{channel} :/timeout {username} {duration}\r\n"
    irc_socket.send(command.encode('utf-8'))
    print(f"[ModBot] Timed out {username} for {duration} seconds.")