from nameko.extensions import DependencyProvider, SharedExtension


class ReplyListener(SharedExtension):

    message_consumer = MessageConsumer()

    def __init__(self, **kwargs):
        super(ReplyListener, self).__init__(**kwargs)

    def setup(self):
        # setup machinery to receieve a reply
        pass

    def stop(self):
        # untangle from Crossbar.io
        # i.e. say goodbye? - or does wampy do this out of the box?
        pass

    def handle_message(self, body, message):
        pass


class WampRpcProxy(DependencyProvider):

    rpc_reply_listener = ReplyListener()

