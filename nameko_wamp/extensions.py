import logging

from nameko.extensions import ProviderCollector, SharedExtension
from wampy.errors import WampyError
from wampy.peers.routers import Crossbar as Router
from wampy.roles.callee import CalleeProxy
from wampy.roles.subscriber import TopicSubscriber

from nameko_wamp.constants import WAMP_CONFIG_KEY
from nameko_wamp.messages import NamekoMessageHandler

logger = logging.getLogger(__name__)


class WampTopicProxy(SharedExtension, ProviderCollector):

    # the only transport supported by Wampy
    transport = "websocket"

    def __init__(self):
        super(WampTopicProxy, self).__init__()

        self._gt = None
        self._topics = []

    def setup(self):
        self.config_path = self.container.config[
            WAMP_CONFIG_KEY]['config_path']
        self.router = Router(config_path=self.config_path)

    def start(self):
        self._register_topics()
        self.consumer = TopicSubscriber(
            topics=self._topics,
            callback=self.message_handler,
            router=self.router,
        )

        self._gt = self.container.spawn_managed_thread(self._consume)

    def stop(self):
        self.consumer.stop()

    def message_handler(self, *args, **kwargs):
        message = kwargs['message']
        topic = kwargs['meta']['topic']

        for provider in self._providers:
            # alternatively could mark providers with subscription IDs?
            if provider.topic == topic:
                provider.handle_message(message)

    def _register_topics(self):
        for provider in self._providers:
            self._topics.append(provider.topic)

    def _consume(self):
        logger.info(
            'WampTopicProxy starting to consume: "%s"', self._topics)
        self.consumer.start()


class WampCalleeProxy(SharedExtension, ProviderCollector):

    def __init__(self):
        super(WampCalleeProxy, self).__init__()

        self._gt = None
        self._procedure_callback_map = {}

    @property
    def procedure_names(self):
        return self._procedure_callback_map.keys()

    def setup(self):
        self._register_procedures()

        self.config_path = self.container.config[
            WAMP_CONFIG_KEY]['config_path']
        self.router = Router(config_path=self.config_path)
        # remember that the CalleeProxy is the WAMP client, not the
        # nameko Extension
        self.client = CalleeProxy(
            router=self.router,
            procedure_names=self.procedure_names,
            callback=self.message_handler,
            message_handler=NamekoMessageHandler,
        )

    def start(self):
        self._gt = self.container.spawn_managed_thread(self._consume)

    def stop(self):
        self.client.stop()

    def message_handler(self, **message):
        meta = message.pop("meta")
        procedure_name = meta['procedure_name']
        request_id = meta['request_id']

        for provider in self._providers:
            if provider.method_name == procedure_name:
                # this is an async operation and only "promises" to return
                # something
                provider.handle_message(message, request_id=request_id)
                break
        else:
            raise WampyError('no providers matching procedure_name')

    def _register_procedures(self):
        for provider in self._providers:
            self._procedure_callback_map[
                provider.method_name] = provider.handle_message

    def _consume(self):
        self.client.start()
