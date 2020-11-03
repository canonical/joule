import logging

from abc import ABC, abstractmethod
from time import sleep
from typing import Iterator, Optional

from autoscale.events import Events, Event


class BaseProvider(ABC):
    """
    Base Provider class.

    Inherit for shared methods.
    """

    @abstractmethod
    def mark_essential(self, *applications: object) -> None:
        """
        :param: application: BaseApplication
        :return: None
        """
        return

    @abstractmethod
    def get_events_from_message_queue(self) -> Iterator[Optional[Event]]:
        """
        :return: Event
        """
        return

    @abstractmethod
    def send_token_to_message_queue(self, event: Event, token: str) -> None:
        """
        :param event: Event
        :param token: String
        :return: None
        """
        return

    def loop(self, *applications: object):
        """
        Loop indefinitely, check for events and act upon them.

        :param applications: BaseApplication
        :return: None
        """
        while True:

            self.mark_essential(*applications)

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
