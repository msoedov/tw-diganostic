
import requests_mock
from app import _run, yaspin


def reply(name="cache", version="v1", rc=10, sc=9):
    return {
        "Application": name,
        "Version": version,
        "Request_Count": rc,
        "Success_Count": sc,
    }


def test_run_empty():
    assert _run([], 2, yaspin.yaspin()) == {}


def test_run_batch():
    with requests_mock.mock() as m:
        m.get("http://one.twitter.com/status", json=reply(sc=9))
        m.get("http://two.twitter.com/status", json=reply(sc=7))
        m.get("http://tree.twitter.com/status", json=reply(sc=8, version="v2"))
        expected = _run(["one", "two", "tree"], 2, yaspin.yaspin())
        assert expected != {}
        assert expected["cache:v1"].rate == 0.8
        assert expected["cache:v2"].rate == 0.8


def test_run_with_err():
    with requests_mock.mock() as m:
        m.get("http://one.twitter.com/status", json=reply(sc=9))
        m.get("http://tree.twitter.com/status", json=reply(sc=8, version="v2"))
        expected = _run(["one", "two", "tree"], 2, yaspin.yaspin())
        assert expected != {}
        assert expected["cache:v1"].rate == 0.9
        assert expected["cache:v2"].rate == 0.8
