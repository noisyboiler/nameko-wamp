import pytest
from wampy.constants import DEFAULT_REALM, DEFAULT_HOST, DEFAULT_PORT
from wampy.peers.clients import Client

from nameko_wamp.extension import WampMessageConsumer



@pytest.yield_fixture
def wamp_client(router):
    with Client() as client:
        yield


def test_foo(router, wamp_client):
    consumer = WampMessageConsumer(
    	router=router, realm=DEFAULT_REALM, topic="foobar",
    	wamp_host=DEFAULT_HOST, wamp_port=DEFAULT_PORT, 
    )

    consumer.start()
    wamp_client.publish(topic="foobar", message="spam")
    consumer.stop()
