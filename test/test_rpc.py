from nameko.testing.utils import assert_stops_raising, get_container
from nameko.testing.services import entrypoint_hook
from wampy.peers.clients import Client

from nameko_wamp.constants import WAMP_CONFIG_KEY
from nameko_wamp.testing import (
    wait_for_registrations, wait_for_subscriptions,
    wait_for_session
)


from test.services import WampServiceA, WampServiceB


def test_nameko_service_rpc_methods_are_called_by_any_wampy_client(
    runner_factory, router, config_path
):

    wamp_client = Client(router=router)

    config = {
        WAMP_CONFIG_KEY: {
            'config_path': config_path,
        }
    }

    runner = runner_factory(config, WampServiceA)
    runner.start()

    assert WampServiceA.messages == []

    container = get_container(runner, WampServiceA)

    with wamp_client as client:
        wait_for_session(client)
        wait_for_registrations(container, number_of_registrations=1)
        wait_for_subscriptions(container, number_of_subscriptions=2)

        result = client.rpc.spam_call(cheese="cheddar", eggs="ducks")

    assert result == "spam"

    def waiting_for_the_message():
        assert len(WampServiceA.messages) == 1
        assert WampServiceA.messages == [
            ((), {u'cheese': u'cheddar', u'eggs': u'ducks'})
        ]

    assert_stops_raising(waiting_for_the_message)

    container.stop()
    WampServiceA.messages = []


def test_nameko_services_can_call_each_other_over_wamp_rpc(
        runner_factory, config_path, router
):
    config = {
        WAMP_CONFIG_KEY: {
            'config_path': config_path,
        }
    }

    runner = runner_factory(config, WampServiceA, WampServiceB)
    runner.start()

    containerA = get_container(runner, WampServiceA)
    wait_for_registrations(containerA, number_of_registrations=1)
    wait_for_subscriptions(containerA, number_of_subscriptions=2)

    containerB = get_container(runner, WampServiceB)
    wait_for_registrations(containerB, number_of_registrations=1)

    with entrypoint_hook(containerB, "service_a_caller") as entrypoint:
        assert entrypoint("value") == "spam"

    runner.stop()
    WampServiceA.messages = []
