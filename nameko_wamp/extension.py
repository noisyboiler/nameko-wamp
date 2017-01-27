import logging

from wampy.peers.routers import Router
from wampy.roles.subscriber import TopicSubscriber

from nameko.extensions import ProviderCollector, SharedExtension

from nameko_wamp.constants import WAMP_CONFIG_KEY

logger = logging.getLogger(__name__)


class WampTopicConsumer(SharedExtension, ProviderCollector):

    def __init__(self):
        super(WampTopicConsumer, self).__init__()

        self._gt = None
        self._topics = []

    def setup(self):
        self.realm = self.container.config[WAMP_CONFIG_KEY]['realm']
        self.wamp_host = self.container.config[WAMP_CONFIG_KEY]['host']
        self.wamp_port = self.container.config[WAMP_CONFIG_KEY]['port']
        self.transport = "websocket"
        self.router = Router(host=self.wamp_host, port=self.wamp_port)


    def start(self):
        self._register_handlers()
        self.consumer = TopicSubscriber(
            router=self.router, realm=self.realm, topics=self._topics,
            transport=self.transport, message_handler=self.message_handler,
        )

        self._gt = self.container.spawn_managed_thread(self._consume)

    def stop(self):
        self.consumer.stop()

    def message_handler(self, *args, **kwargs):
        for provider in self._providers:
            if provider.topic == args[0]:
                logger.info(
                    "nameko extension handling message for %s: %s", provider, (args, kwargs))
                provider.handle_message(*args, **kwargs)

    def _register_handlers(self):
        for provider in self._providers:
            self._topics.append(provider.topic)

    def _consume(self):
        logger.info(
            'TopicSubscriber starting to consume: "%s"', self._topics)
        self.consumer.start()
