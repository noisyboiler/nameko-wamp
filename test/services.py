from nameko_wamp.extensions.dependencies import Caller, Publisher
from nameko_wamp.extensions.entrypoints import consume, callee


class WampSubscriber(object):
    name = "nameko wamp subscriber"

    messages = []

    @consume(topic="foo")
    def foo_handler(self, *args, **kwargs):
        self.messages.append((args, kwargs))

    @consume(topic="bar")
    def bar_handler(self, *args, **kwargs):
        self.messages.append((args, kwargs))


class WampPublisher(object):
    name = "nameko wamp publisher"

    publisher = Publisher()

    @callee
    def publish_foo(self):
        self.publisher(topic="foo", message="hello foo")


class WampServiceA(object):
    name = "wamp service A"

    messages = []

    @consume(topic="foo")
    def foo_handler(self, *args, **kwargs):
        self.messages.append((args, kwargs))

    @consume(topic="bar")
    def bar_handler(self, *args, **kwargs):
        self.messages.append((args, kwargs))

    @callee
    def spam_call(self, *args, **kwargs):
        self.messages.append((args, kwargs))
        return "spam"


class WampServiceB(object):
    name = "wamp service B"

    # note that we don't care about a particular service here
    wamp_caller = Caller()

    @callee
    def service_a_caller(self, *args, **kwargs):
        return self.wamp_caller.spam_call()
