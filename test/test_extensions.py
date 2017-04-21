import pytest
from nameko.testing.utils import assert_stops_raising, get_container
from nameko.testing.services import entrypoint_hook
from wampy.peers.clients import Client

from nameko_wamp.extensions.dependencies import Caller, Pubisher
from nameko_wamp.extensions.entrypoints import consume, callee
from nameko_wamp.constants import WAMP_CONFIG_KEY
from nameko_wamp.testing import (
    wait_for_registrations, wait_for_subscriptions)


class WampServiceA(object):
    name = "wamp service A"

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


class WampServiceB(object):
    name = "wamp service B"

    # note that we don't care about a particular service here
    wamp_caller = Caller()

    @callee
    def service_a_caller(self, *args, **kwargs):
        return self.wamp_caller.spam_call()


class WampServiceC(object):
    name = "wamp service C"

    publisher = Pubisher()

    @callee
    def publish_foo(self):
        self.publisher(topic="foo", message="much ado about foo")


@pytest.yield_fixture
def wamp_client(router):
    with Client(router=router) as client:
        yield client


def test_service_consumes_topics(container_factory, config_path, router):
    container = container_factory(WampServiceA, config={
        WAMP_CONFIG_KEY: {
            'config_path': config_path,
            }
        }
    )

    assert WampServiceA.messages == []

    container.start()
    wait_for_registrations(container, number_of_registrations=1)
    wait_for_subscriptions(container, number_of_subscriptions=2)

    with Client(router=router) as wamp_client:
        wamp_client.publish(topic="foo", message="cheese")
        wamp_client.publish(topic="bar", message="eggs")

    def waiting_for_the_message():
        assert len(WampServiceA.messages) == 2
        assert WampServiceA.messages == [
            ((u'cheese',), {}), ((u'eggs',), {})
        ]

    assert_stops_raising(waiting_for_the_message)
    WampServiceA.messages = []


def test_service_rpc_methods_are_called_from_wamp_client(
        container_factory, config_path, router
):
    container = container_factory(WampServiceA, config={
        WAMP_CONFIG_KEY: {
            'config_path': config_path,
            }
        }
    )

    assert WampServiceA.messages == []

    container.start()
    wait_for_registrations(container, number_of_registrations=1)
    wait_for_subscriptions(container, number_of_subscriptions=2)

    with Client(router=router) as wamp_client:
        result = wamp_client.rpc.spam_call(cheese="cheddar", eggs="ducks")
        assert result == "spam"

    def waiting_for_the_message():
        assert len(WampServiceA.messages) == 1
        assert WampServiceA.messages == [
            (({u'cheese': u'cheddar', u'eggs': u'ducks'},), {})
        ]

    assert_stops_raising(waiting_for_the_message)
    WampServiceA.messages = []


def test_rpc_service_integration(runner_factory, config_path, router):
    config = {
        WAMP_CONFIG_KEY: {
            'config_path': config_path,
        }
    }

    runner = runner_factory(config, WampServiceA, WampServiceB)
    runner.start()

    container = get_container(runner, WampServiceA)
    wait_for_registrations(container, number_of_registrations=1)
    wait_for_subscriptions(container, number_of_subscriptions=2)

    container = get_container(runner, WampServiceB)
    wait_for_registrations(container, number_of_registrations=1)

    with entrypoint_hook(container, "service_a_caller") as entrypoint:
        assert entrypoint("value") == "spam"

    WampServiceA.messages = []


def test_publish_service_integration(runner_factory, config_path, router):
    config = {
        WAMP_CONFIG_KEY: {
            'config_path': config_path,
        }
    }

    runner = runner_factory(config, WampServiceA, WampServiceC)
    runner.start()

    container = get_container(runner, WampServiceA)
    wait_for_registrations(container, number_of_registrations=1)
    wait_for_subscriptions(container, number_of_subscriptions=2)

    assert WampServiceA.messages == []

    container = get_container(runner, WampServiceC)
    with entrypoint_hook(container, "publish_foo") as entrypoint:
        entrypoint()

    def waiting_for_the_message():
        assert len(WampServiceA.messages) == 1
        assert WampServiceA.messages == [
            ((u'much ado about foo',), {})
        ]

    assert_stops_raising(waiting_for_the_message)
    WampServiceA.messages = []
