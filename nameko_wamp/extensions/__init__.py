import logging

from nameko.extensions import ProviderCollector, SharedExtension, Extension
from wampy.errors import WampyError
from wampy.peers.clients import Client
from wampy.peers.routers import Crossbar as Router
from wampy.roles.callee import CalleeProxy
from wampy.roles.subscriber import TopicSubscriber

from nameko_wamp.constants import WAMP_CONFIG_KEY
from nameko_wamp.messages import NamekoMessageHandler

logger = logging.getLogger(__name__)


class WampClientProxy(Extension):

    def setup(self):
        self.config_path = self.container.config[
            WAMP_CONFIG_KEY]['config_path']
        self.router = Router(config_path=self.config_path)
        self.client = Client(
            router=self.router, name="nameko-wamp client proxy"
        )

    def start(self):
        self.client.start()

    def stop(self):
        try:
            self.client.stop()
        except AttributeError:
            pass


class WampTopicProxy(SharedExtension, ProviderCollector):

    def setup(self):
        self.name = "{}: TopicProxy".format(self.container.service_cls.name)

        self._gt = None
        self._topics = []
        self.config_path = self.container.config[
            WAMP_CONFIG_KEY]['config_path']
        self.router = Router(config_path=self.config_path)

    def start(self):
        self._register_topics()
        self.client = TopicSubscriber(
            topics=self._topics,
            callback=self.message_handler,
            router=self.router,
            name=self.name,
        )

        self._gt = self.container.spawn_managed_thread(self._consume)

    def stop(self):
        try:
            self.client.stop()
        except AttributeError:
            pass

        self._gt = None

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
        self.client.start()


class WampCalleeProxy(SharedExtension, ProviderCollector):

    @property
    def procedure_names(self):
        return self._procedure_callback_map.keys()

    def setup(self):
        self.name = "{}: CalleeProxy".format(self.container.service_cls.name)
        logger.info("setting up WampCalleeProxy for: %s", self.name)

        self._gt = None
        self._procedure_callback_map = {}

    def start(self):
        # we need all entrypoints setup methods to have executed before we can
        # compile a list of procedure names
        self._register_procedures()
        if not self.procedure_names:
            logger.warning(
                "At least one proceure must be registered by: %s", self.name
            )

        self.config_path = self.container.config[
            WAMP_CONFIG_KEY]['config_path']

        self.router = Router(config_path=self.config_path)
        self.client = CalleeProxy(
            router=self.router,
            procedure_names=self.procedure_names,
            callback=self.message_handler,
            message_handler=NamekoMessageHandler,
            name=self.name,
        )

        self._gt = self.container.spawn_managed_thread(self._consume)

    def stop(self):
        try:
            self.client.stop()
        except AttributeError:
            pass

        self._gt = None

    def message_handler(self, **message):
        meta = message.pop("meta")
        procedure_name = meta['procedure_name']
        request_id = meta['request_id']

        for provider in self._providers:
            if provider.method_name == procedure_name:
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
