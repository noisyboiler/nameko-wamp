from wampy.messages.handler import MessageHandler
from wampy.messages.invocation import InvocationWithMeta
from wampy.messages import Error, Goodbye, Registered, Welcome


class NamekoInvocation(InvocationWithMeta):

    def handle_result(self, result, error=None):
        # overridden so that a nameko worker thread can handle the result
        pass


class NamekoMessageHandler(MessageHandler):

    def __init__(self, client):
        super(NamekoMessageHandler, self).__init__(
            client=client, messages_to_handle=[
                NamekoInvocation, Welcome, Registered, Goodbye, Error
            ]
        )
