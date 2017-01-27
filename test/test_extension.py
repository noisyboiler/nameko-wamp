import eventlet
import pytest
from wampy.constants import DEFAULT_REALM, DEFAULT_HOST, DEFAULT_PORT
from wampy.peers.clients import Client

from nameko.testing.utils import assert_stops_raising

from nameko_wamp.constants import WAMP_CONFIG_KEY
from nameko_wamp.entrypoint import consume


class WampService(object):
    name = "wamp service"

    messages = []

    @consume(topic="foobar")
    def foobar_handler(self, *args, **kwargs):
        self.messages.append((args, kwargs))

    @consume(topic="spam")
    def spam_handler(self, *args, **kwargs):
        self.messages.append((args, kwargs))


@pytest.yield_fixture
def wamp_client(router):
    with Client() as client:
        yield client


def test_service(container_factory, router):
    container = container_factory(WampService, config={
        WAMP_CONFIG_KEY: {
            'realm': DEFAULT_REALM,
            'topic': "foobar",
            'host': DEFAULT_HOST,
            'port': DEFAULT_PORT,
            }
        }
    )

    assert WampService.messages == []

    container.start()

    # wait a couple of seconds for the subscription to take place...
    # how better to handle this?
    eventlet.sleep(2)

    with Client() as wamp_client:
        wamp_client.publish(topic="foobar", message="spam")
        wamp_client.publish(topic="spam", message="cheese")

    def waiting_for_the_message():
        assert len(WampService.messages) == 2

    assert_stops_raising(waiting_for_the_message)
