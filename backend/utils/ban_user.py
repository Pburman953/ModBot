


def ban_user(irc_socket, channel, username):
    """
    Bans a user from the Twitch channel.
    """
    command = f"PRIVMSG #{channel} :/ban {username}\r\n"
    irc_socket.send(command.encode('utf-8'))
    print(f"[ModBot] Banned {username}.")