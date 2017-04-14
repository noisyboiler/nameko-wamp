import pytest
from nameko.testing.utils import assert_stops_raising
from wampy.peers.clients import Client

from nameko_wamp.constants import WAMP_CONFIG_KEY
from nameko_wamp.entrypoints import consume, callee
from nameko_wamp.testing import wait_for_registrations


class WampService(object):
    name = "wamp service"

    messages = []

    @consume(topic="foo")
    def foo_handler(self, *args, **kwargs):
        self.messages.append((args, kwargs))

    @consume(topic="bar")
    def bar_handler(self, *args, **kwargs):
        self.messages.append((args, kwargs))

    @callee
    def spam_call(self, *args, **kwargs):
        self.messages.append((args, kwargs))
        return "spam"


@pytest.yield_fixture
def wamp_client(router):
    with Client(router=router) as client:
        yield client


def test_service_consumes_topics(container_factory, config_path, router):
    container = container_factory(WampService, config={
        WAMP_CONFIG_KEY: {
            'config_path': config_path,
            }
        }
    )

    assert WampService.messages == []

    container.start()

    with Client(router=router) as wamp_client:
        wamp_client.publish(topic="foo", message="cheese")
        wamp_client.publish(topic="bar", message="eggs")

    def waiting_for_the_message():
        assert len(WampService.messages) == 2
        assert WampService.messages == [
            ((u'cheese',), {}), ((u'eggs',), {})
        ]

    assert_stops_raising(waiting_for_the_message)
    WampService.messages = []


def test_service_rpc_methods_are_called_from_wamp_client(
        container_factory, config_path, router
):
    container = container_factory(WampService, config={
        WAMP_CONFIG_KEY: {
            'config_path': config_path,
            }
        }
    )

    assert WampService.messages == []

    container.start()
    wait_for_registrations(container, number_of_registrations=1)

    with Client(router=router) as wamp_client:
        result = wamp_client.rpc.spam_call(cheese="cheddar", eggs="ducks")
        assert result == "spam"

    def waiting_for_the_message():
        assert len(WampService.messages) == 1
        assert WampService.messages == [
            (({u'cheese': u'cheddar', u'eggs': u'ducks'},), {})
        ]

    assert_stops_raising(waiting_for_the_message)
    WampService.messages = []
