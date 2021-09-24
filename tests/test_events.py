from joule import events


def test_enum():
    """
    Assert we've not accidentally changed events.
    """
    e = events.Events

    assert e.JOIN
    assert e.LAUNCH
    assert e.TERMINATE


def test_new_join_event():
    """
    Test init of new JOIN event.
    """
    e = events.Events

    a = events.Event(e.JOIN, "cloud-1", {"pay": "load"}, None)

    assert a.event == e.JOIN
    assert a.instance == "cloud-1"
    assert a.payload == {"pay": "load"}
    assert a.application == None


def test_new_launch_event():
    """
    Test init of new LAUNCH event.
    """
    e = events.Events

    a = events.Event(e.LAUNCH, "cloud-1", {"pay": "load"}, None)

    assert a.event == e.LAUNCH
    assert a.instance == "cloud-1"
    assert a.payload == {"pay": "load"}
    assert a.application == None


def test_new_terminate_event():
    """
    Test init of new TERMINATE event.
    """
    e = events.Events

    a = events.Event(e.TERMINATE, "cloud-1", {"pay": "load"}, None)

    assert a.event == e.TERMINATE
    assert a.instance == "cloud-1"
    assert a.payload == {"pay": "load"}
    assert a.application == None
