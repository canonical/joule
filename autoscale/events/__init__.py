from enum import Enum
from typing import Optional


class Events(Enum):
    """
    Enumeration of possible events.
    """

    JOIN = 0
    LAUNCH = 1
    TERMINATE = 2


class Event:
    """
    Event instance.

    This is used to abstract provider specific events into simpler primitives.
    """

    def __init__(self, event: Enum, instance: str, token: Optional[str] = None) -> None:
        """
        :param event: Event object from queue
        :param instance: String cloud provider instance id
        :param token: String used to join instance to the application cluster
        :return: None
        """
        self.event: Enum = event
        self.instance: str = instance
        self.token: Optional[str] = token
