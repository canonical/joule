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

    def __init__(
        self,
        event: Events,
        instance: str,
        payload: Optional[dict] = None,
        application: Optional[object] = None,
    ) -> None:
        """
        :param event: Event object from queue
        :param instance: String cloud provider instance id
        :param payload: Dictionary usually used to join instance to the application cluster
        :param application: BaseApplication to lock event to
        :return: None
        """
        self.event: Events = event
        self.instance: str = instance
        self.payload: Optional[dict] = payload
        self.application: Optional[object] = application
