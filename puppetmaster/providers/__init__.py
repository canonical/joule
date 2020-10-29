import logging

from abc import ABC
from time import sleep
from typing import Iterator, List, Optional
from subprocess import check_output

from puppetmaster.events import Events, Event


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

    def loop(self, applications: List[object]):
        """
        Loop indefinitely, check for events and act upon them.

        :return: None
        """
        while True:
            for event in self.get_events_from_message_queue():
                if event.event is Events.JOIN:
                    logging.info("JOIN event.")
                    for app in applications:
                        app.join(self, event)

                elif event.event is Events.LAUNCH:
                    logging.info("LAUNCH event.")
                    for app in applications:
                        app.launch(self, event)

                elif event.event is Events.TERMINATE:
                    logging.info("TERMINATE event.")
                    for app in applications:
                        app.terminate(self, event)
                else:
                    sleep(1)
                    continue
