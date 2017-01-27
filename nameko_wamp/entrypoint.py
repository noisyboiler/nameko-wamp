from nameko.extensions import Entrypoint

from nameko_wamp.extension import WampTopicConsumer


class WampTopicEntrypoint(Entrypoint):
    topic_consumer = WampTopicConsumer()

    def __init__(self, topic):
        self.topic = topic

    def setup(self):
        self.topic_consumer.register_provider(self)

    def stop(self):
        self.topic_consumer.unregister_provider(self)

    def handle_message(self, *args, **kwargs):
        self.container.spawn_worker(self, args, kwargs)


consume = WampTopicEntrypoint.decorator
