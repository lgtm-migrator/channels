from .base import socket_io

"""
Module containing Socket.IO emitting or callback functions.
"""

def announce_channel(channel_name: str) -> None:
    """Emit information about the channel that was added to DB.

    Args:
        channel_name: Name of the channel that was added.

    """
    response = {'channelName': channel_name}
    socket_io.emit('announce channel', response, broadcast=True)

def announce_message(user: str, time: str, channel: str, message_content: str) -> None:
    """Emit all information about the message that was added to DB.

    Args:
        user: Name of the user who sent the message.
        time: Time when she/he sent it.
        channel: Channel the message was sent to.
        message_content: Content of the message.

    """
    response = {
        'user': user,
        'time': time,
        'channel': channel,
        'messageContent': message_content
    }
    socket_io.emit('announce message', response, broadcast=True)