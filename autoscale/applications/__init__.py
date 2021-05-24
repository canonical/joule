import logging

from abc import ABC, abstractmethod

from autoscale.events import Events, Event
from autoscale.providers import BaseProvider


class BaseApplication(ABC):
    """
    Base Application class.

    These methods are required in order to provide support for any application
    you want to be automatically scaled.

    The inheriting class will then be operated by the provider's main loop.
    """

    @abstractmethod
    def is_essential(self) -> bool:
        """
        Use if the application needs to protect certain instances from
        termination during scale in.  May be omitted, in which case the
        return value will always be False.

        :return: Boolean is node essential / protect from scale in
        """
        return False

    @abstractmethod
    def join(self, provider: BaseProvider, event: Event) -> None:
        """
        Called after a new instance has started and is only handled on the new
        instance.  Use this for any configuration that needs to be done to the
        application to join the cluster.  For example, passing a token to the
        application in order to authenticate it into application's the
        cluster.

        :param provider: BaseProvider instance of specific cloud
        :param event: Event object from queue
        :return: None
        """

    @abstractmethod
    def launch(self, provider: BaseProvider, event: Event) -> None:
        """
        Called when a new instance has been launched by the provider.  Use
        this for handling any actions required before the new instance are
        joined to the cluster.  It could be run on any existing instance in
        the cluster.  For example, adding the new instance to a list of
        allowed hosts.

        :param provider: BaseProvider instance of specific cloud
        :param event: Event object from queue
        :return: None
        """

    @abstractmethod
    def terminate(self, provider: BaseProvider, event: Event) -> None:
        """
        Called when an instance is terminated.  Use this to cleanup anything
        within the cluster after termination of an existing instance.  It
        could be run on any existing instance on the cluster.  For example,
        removing the instance from a list of allowed hosts.

        :param provider: BaseProvider instance of specific cloud
        :param event: Event object from queue
        :return: None
        """