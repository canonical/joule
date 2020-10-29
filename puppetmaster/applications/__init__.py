import logging

from abc import ABC

from puppetmaster.events import Events, Event
from puppetmaster.providers import BaseProvider


class BaseApplication(ABC):
    """
    Base Application class.

    Inherit for shared methods.
    """

    def __init__(self):
        raise NotImplementedError("Must use a real application.")

    def join(self, provider: BaseProvider, event: Event) -> None:
        raise NotImplementedError("Must use a real application.")

    def launch(self, provider: BaseProvider, event: Event) -> None:
        raise NotImplementedError("Must use a real application.")

    def terminate(self, provider: BaseProvider, event: Event) -> None:
        raise NotImplementedError("Must use a real application.")
