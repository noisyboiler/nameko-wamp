from nameko.extensions import Entrypoint

from nameko_wamp.extension import WampTopicConsumer


class WampTopicHandler(Entrypoint):
    topic_consumer = WampTopicConsumer()

    def __init__(self, topic):
        self.topic = topic

    def setup(self):
        self.topic_consumer.register_provider(self)

    def stop(self):
        self.topic_consumer.unregister_provider(self)

    def handle_message(self, *args, **kwargs):
        instance = self.container.service_cls()
        method = getattr(instance, self.method_name)
        method(*args, **kwargs)


consume = WampTopicHandler.decorator
