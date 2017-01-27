import logging

from wampy.peers.routers import Router
from wampy.roles.subscriber import TopicSubscriber

from nameko.extensions import ProviderCollector, SharedExtension

from nameko_wamp.constants import WAMP_CONFIG_KEY

logger = logging.getLogger(__name__)


class WampTopicConsumer(SharedExtension, ProviderCollector):

    # the only transport supported by Wampy
    transport = "websocket"

    def __init__(self):
        super(WampTopicConsumer, self).__init__()

        self._gt = None
        self._topics = []

    def setup(self):
        self.realm = self.container.config[WAMP_CONFIG_KEY]['realm']
        self.wamp_host = self.container.config[WAMP_CONFIG_KEY]['host']
        self.wamp_port = self.container.config[WAMP_CONFIG_KEY]['port']
        self.router = Router(host=self.wamp_host, port=self.wamp_port)

    def start(self):
        self._register_topics()
        self.consumer = TopicSubscriber(
            router=self.router, realm=self.realm, topics=self._topics,
            transport=self.transport, message_handler=self.message_handler,
        )

        self._gt = self.container.spawn_managed_thread(self._consume)

    def stop(self):
        self.consumer.stop()

    def message_handler(self, *args, **kwargs):
        message = kwargs['message']
        topic = kwargs['_meta']['topic']

        for provider in self._providers:
            if provider.topic == topic:
                provider.handle_message(message)

    def _register_topics(self):
        for provider in self._providers:
            self._topics.append(provider.topic)

    def _consume(self):
        logger.info(
            'TopicSubscriber starting to consume: "%s"', self._topics)
        self.consumer.start()
