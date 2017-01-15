from wampy.peers.routers import Router
from wampy.roles.subscriber import TopicSubscriber

from nameko.extensions import SharedExtension


# look at the QueueConsumer in nameko core
class WampMessageConsumer(SharedExtension):
    """ Managed by the Container and responsible for consuming
    WAMP messages off the server.

    ``SharedExtension`` gives us a lookup to the Container that we will
    be running in.

    """
    def __init__(
            self, router, realm, topic,
            wamp_host=None, wamp_port=None, transport="websocket"
    ):

        super(WampMessageConsumer, self).__init__()

        self.router = router
        self.realm = realm
        self.topic = topic
        self.wamp_host = wamp_host or self.container.config[WAMP_URI_CONFIG_KEY]['host']
        self.wamp_port = wamp_port or self.container.config[WAMP_URI_CONFIG_KEY]['port']
        self.transport = transport
        self.router = Router(host=self.wamp_host, port=self.wamp_port)
        self.messages = []

        self._gt = None

    def setup(self):
        self.consumer = TopicSubscriber(
            router=self.router, realm=self.realm, topic=self.topic,
            transport=self.transport,
        )

    def start(self):
        self._gt = self.container.spawn_managed_thread(self._consume)

    def stop(self):
        self.consumer.stop()

    def _consume(self):
        self.consumer.start()
