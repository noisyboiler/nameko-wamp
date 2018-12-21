import logging

from nameko.extensions import (
    DependencyProvider, ProviderCollector, SharedExtension, Extension)
from wampy.message_handler import MessageHandler
from wampy.roles.caller import RpcProxy
from wampy.peers.clients import Client
from wampy.peers.routers import Crossbar as Router
from wampy.roles.publisher import PublishProxy

from nameko_wamp.constants import WAMP_CONFIG_KEY
from nameko_wamp.wamp import NamekoWampyClient, NamekoMessageHandler

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
        self.name = "{} TopicProxy".format(self.container.service_cls.name)
        logger.info("%s WampTopicProxy setting up", self.name)

        self._gt = None
        self._topics = []
        self.config_path = self.container.config[
            WAMP_CONFIG_KEY]['config_path']
        self.router = Router(config_path=self.config_path)

    def start(self):
        # we need all entrypoints setup methods to have executed before we can
        # compile a list of topics to subscribe to
        self._register_topics()
        if not self._topics:
            logger.warning(
                "At least one topic should be subscribed to by: %s", self.name
            )

        logger.info("registering topics: %s", self._topics)
        self.client = NamekoWampyClient(
            providers=self._providers,
            topics=self._topics,
            router=self.router,
            message_handler=MessageHandler(),
            name=self.name,
        )

        self._gt = self.container.spawn_managed_thread(self._consume)

    def stop(self):
        try:
            self.client.stop()
        except AttributeError:
            pass

        self._gt = None

    def _register_topics(self):
        for provider in self._providers:
            self._topics.append(provider.topic)

    def _consume(self):
        self.client.start()


class WampCalleeProxy(SharedExtension, ProviderCollector):

    def setup(self):
        self.name = "{}: CalleeProxy".format(self.container.service_cls.name)
        logger.info("setting up WampCalleeProxy for: %s", self.name)

        self._gt = None
        self._procedures = []

        self.config_path = self.container.config[
            WAMP_CONFIG_KEY]['config_path']
        self.router = Router(config_path=self.config_path)

    def start(self):
        # we need all entrypoints setup methods to have executed before we can
        # compile a list of procedure names
        self._register_procedures()
        if not self._procedures:
            logger.warning(
                "At least one proceure should be registered by: %s", self.name
            )

        self.client = NamekoWampyClient(
            providers=self._providers,
            router=self.router,
            procedures=self._procedures,
            message_handler=NamekoMessageHandler(),
            name=self.name,
        )

        self._gt = self.container.spawn_managed_thread(self._consume)

    def stop(self):
        try:
            self.client.stop()
        except AttributeError:
            pass

        self._gt = None

    def _register_procedures(self):
        for provider in self._providers:
            self._procedures.append(provider.method_name)

    def _consume(self):
        self.client.start()


class Caller(DependencyProvider):

    proxy = WampClientProxy()

    def get_dependency(self, worker_ctx):
        call_proxy = RpcProxy(client=self.proxy.client)
        return call_proxy


class Publisher(DependencyProvider):

    proxy = WampClientProxy()

    def get_dependency(self, worker_ctx):
        publish_proxy = PublishProxy(client=self.proxy.client)
        return publish_proxy
