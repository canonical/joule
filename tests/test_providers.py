import pytest

from joule.providers import BaseProvider


def test_abstract_base_class_empty():
    """
    Test the abstract base class doesn't initialize without methods.
    """

    class TestProvider(BaseProvider):
        pass

    with pytest.raises(TypeError):
        TestProvider()


def test_abstract_base_class_complete():
    """
    Test the abstract base class.
    """

    class TestProvider(BaseProvider):
        def __init__(self, application=None):
            super().__init__(application)

        def mark_essential(self):
            return

        def mark_enrolled(self):
            return

        def is_enrolled(self):
            return True

        def get_events_from_message_queue(self):
            return

        def send_join_to_message_queue(self):
            return

    a = TestProvider()
    assert a.is_enrolled() is True
