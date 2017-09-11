import logging
from functools import partial

from nameko.extensions import Entrypoint
from wampy.messages import Yield

from .dependencies import WampTopicProxy, WampCalleeProxy

logger = logging.getLogger(__name__)


class WampTopicEntrypoint(Entrypoint):
    topic_consumer = WampTopicProxy()

    def __init__(self, topic):
        self.topic = topic

    def setup(self):
        self.topic_consumer.register_provider(self)

    def stop(self):
        self.topic_consumer.unregister_provider(self)

    def handle_message(self, *args, **kwargs):
        self.container.spawn_worker(self, args, kwargs)


class WampCalleeEntrypoint(Entrypoint):
    callee_proxy = WampCalleeProxy()

    def setup(self):
        logger.info("registering provider: %s", self)
        self.callee_proxy.register_provider(self)

    def stop(self):
        self.callee_proxy.unregister_provider(self)

    def handle_message(self, request_id, *args, **kwargs):
        handle_result = partial(self.handle_result, request_id)
        self.container.spawn_worker(
            self, args, kwargs, handle_result=handle_result
        )

    def handle_result(self, request_id, *args, **kwargs):
        worker_ctx, result, exc_info = args
        session = self.callee_proxy.client.session

        result_kwargs = {}
        result_kwargs['error'] = exc_info
        result_kwargs['message'] = result
        result_kwargs['meta'] = {}
        result_kwargs['meta']['procedure_name'] = (
            worker_ctx.entrypoint.method_name)
        result_kwargs['meta']['session_id'] = session.id

        result_args = [result]

        yield_message = Yield(
            request_id,
            result_args=result_args,
            result_kwargs=result_kwargs,
        )

        session.send_message(yield_message)
        return result, exc_info


consume = WampTopicEntrypoint.decorator
callee = WampCalleeEntrypoint.decorator
