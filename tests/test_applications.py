import pytest

from joule.applications import BaseApplication


def test_abstract_base_class_empty():
    """
    Test the abstract base class doesn't initialize without methods.
    """

    class TestApplication(BaseApplication):
        pass

    with pytest.raises(TypeError):
        TestApplication()


def test_abstract_base_class_no_name():
    """
    Test the abstract base class doesn't initialize without name.
    """

    class TestApplication(BaseApplication):
        def is_essential(self):
            return True

        def join(self):
            return

        def launch(self):
            return

        def terminate(self):
            return

    a = TestApplication()

    with pytest.raises(NotImplementedError):
        a.name


def test_abstract_base_class_complete():
    """
    Test the abstract base class.
    """

    class TestApplication(BaseApplication):
        name = "test"

        def is_essential(self):
            return True

        def join(self):
            return

        def launch(self):
            return

        def terminate(self):
            return

    a = TestApplication()
    assert a.is_essential() is True
    assert a.name == "test"
