from enum import Enum, auto
"""Флаги для handler_get_message.py"""
class Flags(Enum):
    WAITING_FOR_MESSAGE = auto()
    PERS_CHAT_FLAG = auto()
    SELECTING_TOPIC = auto()
    ANSWERING_QUESTION = auto()
    DESCRIBE_PICTURE = auto()
    VOICE_CHAT = auto()
