from nameko.testing.utils import assert_stops_raising, get_container
from nameko.testing.services import entrypoint_hook
from wampy.peers.clients import Client

from nameko_wamp.constants import WAMP_CONFIG_KEY
from nameko_wamp.testing import (
    wait_for_registrations, wait_for_subscriptions)

from test.services import WampSubscriber, WampPublisher


def test_nameko_service_can_subscribe_to_wamp_topic(
    runner_factory, router, config_path
):
    wamp_client = Client(router=router)

    config = {
        WAMP_CONFIG_KEY: {
            'config_path': config_path,
        }
    }

    runner = runner_factory(config, WampSubscriber)
    runner.start()

    container = get_container(runner, WampSubscriber)
    wait_for_subscriptions(container, number_of_subscriptions=2)

    with wamp_client as client:
        client.publish(topic="foo", message="hello foo")
        client.publish(topic="bar", message="hello bar")

    def waiting_for_the_message():
        assert len(WampSubscriber.messages) == 2
        assert sorted(WampSubscriber.messages) == sorted([
            ((u'hello foo',), {}),
            ((u'hello bar',), {})
        ])

    assert_stops_raising(waiting_for_the_message)
    WampSubscriber.messages = []


def test_nameko_services_can_subscribe_to_other_nameko_services(
        runner_factory, config_path, router
):
    config = {
        WAMP_CONFIG_KEY: {
            'config_path': config_path,
        }
    }

    runner = runner_factory(config, WampSubscriber, WampPublisher)
    runner.start()

    container = get_container(runner, WampSubscriber)
    wait_for_subscriptions(container, number_of_subscriptions=2)

    assert WampSubscriber.messages == []

    container = get_container(runner, WampPublisher)
    wait_for_registrations(container, number_of_registrations=1)

    with entrypoint_hook(container, "publish_foo") as entrypoint:
        entrypoint()

    def waiting_for_the_message():
        assert len(WampSubscriber.messages) == 1
        assert WampSubscriber.messages == [
            ((u'hello foo',), {})
        ]

    assert_stops_raising(waiting_for_the_message)
    WampSubscriber.messages = []
