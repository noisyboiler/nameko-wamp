import logging

from wampy.peers.routers import Router
from wampy.roles.subscriber import TopicSubscriber

from nameko.extensions import ProviderCollector, SharedExtension

from nameko_wamp.constants import WAMP_CONFIG_KEY

logger = logging.getLogger(__name__)


class WampTopicConsumer(SharedExtension, ProviderCollector):

    def __init__(self, topic):
        super(WampTopicConsumer, self).__init__()
        self.topic = topic

        self._gt = None

    def setup(self):
        self.realm = self.container.config[WAMP_CONFIG_KEY]['realm']
        self.wamp_host = self.container.config[WAMP_CONFIG_KEY]['host']
        self.wamp_port = self.container.config[WAMP_CONFIG_KEY]['port']
        self.transport = "websocket"
        self.router = Router(host=self.wamp_host, port=self.wamp_port)
        self.consumer = TopicSubscriber(
            router=self.router, realm=self.realm, topic=self.topic,
            transport=self.transport, message_handler=self.message_handler,
        )

    def start(self):
        self._gt = self.container.spawn_managed_thread(self._consume)

    def stop(self):
        self.consumer.stop()

    def message_handler(self, *args, **kwargs):
        for provider in self._providers:
            provider.handle_message(*args, **kwargs)

    def _consume(self):
        logger.info(
            'TopicSubscriber starting to consume: "%s"', self.topic)
        self.consumer.start()
