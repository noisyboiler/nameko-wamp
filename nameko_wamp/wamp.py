import logging
from functools import partial

from wampy.errors import WampyError
from wampy.message_handler import MessageHandler
from wampy.peers.clients import Client

logger = logging.getLogger(__name__)


class NamekoMessageHandler(MessageHandler):

    def handle_invocation(self, message_obj):
        # over-ridden to pass the Request ID through to the nameko service
        # and to remove the call to ``process_result``, leaving the nameko
        # service to do so
        session = self.session

        args = message_obj.call_args
        kwargs = message_obj.call_kwargs

        procedure_name = session.registration_map[
            message_obj.registration_id]
        procedure = getattr(self.client, procedure_name)

        try:
            # notice we don't care about the result here - it is handled
            # in a separate worker thread
            procedure(
                message_obj.request_id, *args, **kwargs
            )
        except Exception:
            logger.exception("error calling: %s", procedure.__name__)
            raise


class NamekoWampyClient(Client):
    def __init__(
        self, providers, topics=None, procedures=None, **kwargs
    ):
        self.providers = providers
        self.topics = topics or []
        self.procedures = procedures or []

        super(NamekoWampyClient, self).__init__(**kwargs)

    def __getattr__(self, name):
        # implemented to intercept calls to callee entrypoints which are not
        # found on the wamp Client (as ususal) but instead on the nameko
        # service
        if name in self.procedures:
            # normally an explicit app or service client would handle this,
            # but with this client, many procedures are handled by one
            # callback.
            return partial(self.callee_callback, name)

        return getattr(self, name)

    def callee_callback(self, procedure_name, *args, **kwargs):
        for provider in self.providers:
            if provider.method_name == procedure_name:
                provider.handle_message(*args, **kwargs)
                break
        else:
            raise WampyError('no providers matching procedure_name')

    def topic_callback(self, *args, **kwargs):
        message = kwargs['message']
        topic = kwargs['meta']['topic']

        for provider in self.providers:
            # alternatively could mark providers with subscription IDs?
            if provider.topic == topic:
                provider.handle_message(message)

    def register_roles(self):
        # over-ridden so that a single handler for all nameko service
        # consumers or callees can act as a proxy to the actual service
        # callable
        logger.info("registering roles for: %s", self.name)
        for topic in self.topics:
            self.session._subscribe_to_topic(self.topic_callback, topic)
            logger.info(
                '%s subscribed to topic "%s"', self.name, topic,
            )

        for procedure_name in self.procedures:
            self.session._register_procedure(procedure_name)
            logger.info(
                '%s registered callee "%s"', self.name, procedure_name,
            )

        logger.info('registered all roles')
