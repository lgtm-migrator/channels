import re
from flask import jsonify, url_for
from flask_login import current_user
from datetime import datetime
from typing import Any

from app.models.base import db
from app.models.channel import Channel
from app.models.message import Message
from app.models.user import User
from ..sockets.sockets import announce_channel, announce_message

"""
Utility functions for main routes.
"""

valid_pattern = re.compile(r'[A-Za-z0-9 \-_]+')

def channel_has_invalid_name(channel_name: str) -> bool:
    """Check if the channel has invalid name. Its name is invalid if either it is empty,
    has trailing or leading spaces, or violates the `valid_pattern` regex.

    Args:
        channel_name: Name of the channel to be checked.

    Returns:
        True if it has invalid name, False otherwise.

    """

    if not channel_name:
        return True
    else:
        return not(bool(re.fullmatch(valid_pattern, channel_name))) \
               or channel_name.startswith(' ') \
               or channel_name.endswith(' ')


def channel_already_exists(channel_name: str) -> bool:
    """Check if the channel already exists in the database.

    Args:
        channel_name: Name of the channel to be checked.

    Returns:
        True if it already exists, false otherwise.

    """
    channel = Channel.query.filter_by(name=channel_name).first()
    return bool(channel)

def add_channel(channel_name: str) -> None:
    """Add channel to the database and emit it with Socket.IO.

    Args:
        channel_name: Name of the channel to be added.

    """
    db.session.add(Channel(name=channel_name))
    db.session.commit()
    announce_channel(channel_name)

def pretty_time(full_time: datetime) -> str:
    """Take datetime object and get its string of the form YYYY-MM-DD HH:MM.

    Args:
        full_time: DateTime object which pretty form the function should return.

    Returns:
        String YYYY-MM-DD HH:MM.

    """
    full_time_str = str(full_time)
    length_boundary = len('2020-01-01 00:00')
    return full_time_str[:length_boundary]

def get_messages(channel_name: str, counter: int) -> Any:
    """Get the messages of the given channel and return them in JSON format.
    The function supports dynamic loading and will return only a specified number of messages.
    The last message to be loaded is given by the argument "counter".

    Args:
        channel_name: Name of the channel which messages the function should look for.
        counter: Id of the last message to be displayed.

    Returns:
        JSON response with all data about messages of the channel.

    """
    num_messages_loaded_at_once = 20

    channel = Channel.query.filter_by(name=channel_name).first()
    messages = channel.messages

    messages_response = [
        {
            'userName': User.query.filter_by(id=message.user_id).first().username,
            'userPicture': f"{url_for('static', filename='img/profile_pictures')}/"
                           f"{ User.query.filter_by(id=message.user_id).first().profile_picture }",
            'content': message.content,
            'time': pretty_time(message.time)
        }
        for message in messages[max(counter - num_messages_loaded_at_once, 0):counter]
    ]
    return jsonify({'messages': messages_response})

def add_message(message_content: str, channel: str) -> None:
    """Add the given message to the given channel in database. Emit the message with Socket.IO
    after adding it.

    Args:
        message_content: Content of the message to be added.
        channel: Channel the message should be added to.

    """
    username = current_user.username
    user_id = current_user.id
    user_picture = f"{url_for('static', filename='img/profile_pictures')}/{ current_user.profile_picture }"

    full_time = datetime.now()

    channel_id = Channel.query.filter_by(name=channel).first().id

    db.session.add(Message(
        content=message_content, user_id=user_id, time=full_time, channel_id=channel_id
    ))

    db.session.commit()
    announce_message(username, user_picture, pretty_time(full_time), channel, message_content)