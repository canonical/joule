import logging

from abc import ABC
from enum import Enum
from time import sleep
from typing import Iterator, Optional
from subprocess import check_output


class Events(Enum):
    """
    Enumeration of possible events.
    """

    JOIN = 0
    LAUNCH = 1
    TERMINATE = 3


class Event:
    """
    Event instance.
    """

    def __init__(self, event: Enum, instance: str, token: Optional[str] = None):
        self.event = event
        self.instance = instance
        self.token = token


class BaseProvider(ABC):
    """
    Base Provider class.

    Inherit for shared methods.
    """

    def __init__(self):
        raise NotImplementedError("Must use a real provider.")

    def get_events_from_message_queue(self) -> Iterator[Optional[Event]]:
        raise NotImplementedError("Must use a real provider.")

    def send_token_to_message_queue(self, event: Event, token: str) -> None:
        raise NotImplementedError("Must use a real provider.")

    def get_token_from_microk8s(self) -> str:
        """
        Run microk8s add-node to generate a token.

        :return: str
        """
        return (
            check_output(["sudo", "microk8s", "add-node", "--token-ttl", "-1"])
            .decode()
            .split()[15]
        )

    def remove_node_from_microk8s(self, event: Event) -> None:
        """
        Run microk8s remove-node on terminiating instance.

        :return: None
        """
        check_output(["sudo", "microk8s", "remove-node", event.instance, "--force"])

    def join_node_to_microk8s(self, event: Event) -> None:
        """
        Run microk8s join to add instance to cluster.
        """
        check_output(["sudo", "microk8s", "join", event.token])

    def loop(self):
        """
        Loop indefinitely, check for events and act upon them.

        :return: None
        """
        while True:
            for event in self.get_events_from_message_queue():
                if event.event is Events.JOIN:
                    logging.info("JOIN event.")
                    self.join_node_to_microk8s(event)

                elif event.event is Events.LAUNCH:
                    logging.info("LAUNCH event.")
                    token = self.get_token_from_microk8s()
                    self.send_token_to_message_queue(event, token)

                elif event.event is Events.TERMINATE:
                    logging.info("TERMINATE event.")
                    self.remove_node_from_microk8s(event)

                else:
                    sleep(1)
                    continue
