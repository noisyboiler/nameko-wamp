from nameko.extensions import Entrypoint

from nameko_wamp.extension import WampTopicExtension


class WampTopicConsumer(Entrypoint):

    topic_consumer = WampTopicExtension()

    def __init__(self, topic):
        """ Decorates a method as a WAMP topic consumer.

        :Parameters:
            topic: string
                The topic to consume from.

        """
        self.topic = topic

    def setup(self):
        self.topic_consumer.register_provider(self)

    def stop(self):
        self.topic_consumer.unregister_provider(self)

    def handle_message(self, body, message):
        # how to get here??
        pass


consume = WampTopicConsumer.decorator
