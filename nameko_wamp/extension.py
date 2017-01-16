import logging

from wampy.peers.routers import Router
from wampy.roles.subscriber import TopicSubscriber

from nameko.extensions import ProviderCollector, SharedExtension

from nameko_wamp.constants import WAMP_CONFIG_KEY 

logger = logging.getLogger(__name__)


class WampTopicExtension(SharedExtension, ProviderCollector):
    """ Consumes WAMP messages from a WAMP "Router" Peer.

    .. note::
        ``SharedExtension`` gives us a lookup to the Container that we will
        be running in.

    .. note::
        Uses ``wampy`` as the WAMP client.

    """
    def __init__(self):
        super(WampTopicExtension, self).__init__()

        self.messages = []
        self._gt = None

    def setup(self):
        self.realm = self.container.config[WAMP_URI_CONFIG_KEY]['realm']
        self.topic = self.container.config[WAMP_URI_CONFIG_KEY]['topic']
        self.wamp_host = self.container.config[WAMP_URI_CONFIG_KEY]['host']
        self.wamp_port = self.container.config[WAMP_URI_CONFIG_KEY]['port']
        self.transport = "websocket"
        self.router = Router(host=self.wamp_host, port=self.wamp_port)
        self.consumer = TopicSubscriber(
            router=self.router, realm=self.realm, topic=self.topic,
            transport=self.transport, message_queue=self.messages,
        )

    def start(self):
        self._gt = self.container.spawn_managed_thread(self._consume)

    def stop(self):
        self.consumer.stop()

    def _consume(self):
        logger.info(
            'TopicSubscriber starting to consume: "%s"', self.topic)
        self.consumer.start()
