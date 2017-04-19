|Travis|_ |Python27|_ 

.. |Travis| image:: https://travis-ci.org/noisyboiler/nameko-wamp.svg?branch=master
.. _Travis: https://travis-ci.org/noisyboiler/nameko-wamp

.. |Python27| image:: https://img.shields.io/badge/python-2.7-blue.svg

nameko wamp
===========

Web Application Messaging Protocol (WAMP) for the nameko microservices framework

Nameko Wamp provides Extensions for WAMP PUB-SUB and RPC. Here is a (silly) example service implementing WAMP entrypoints.

::

    from nameko_wamp.extensions.dependencies import Caller, Publisher
    from nameko_wamp.extensions.entrypoints import consume, callee


    class WeatherService:

        name = "weather_service"

        caller = Caller()
        publihser = Publisher()

        @callee
        def get_weather(self):
            # the weather is always sunny here!
            return "sunny"

        @consume
        def weather_updates(self, topic_data):
            # and do something with the new weather data here
            pass


One method is marked as a "callee", which is a WAMP Role, and another is marked as a WAMP "caller" Role. The former is callable over RPC and is (almost) exactly the same as the nameko ``rpc`` Extension. The latter consumes from a WAMP Topic and appears exactly the same as the nameko ``event_handler`` Extension.

There is also the dependency injection ``caller``. Yet another WAMP Role, this allows outgoing RPC calls from your service to other nameko services. Finally the WAMP Role ``publisher`` dependency which allows a service API to publish messages to WAMP Topics.

Wampy
~~~~~

Under the hood nameko wamp uses wampy as the Client Peer - and the Router Peer when running tests. The Router is Crossbar.io.

You can use a stand-alone wampy Client to interact with your nameko services too. See the wampy project for more details, but the standard pattern is:

::

    with Client(router=router) as client:
        result = client.rpc.get_weather()
        assert result == "sunny"

        # and publish to a Topic
        client.publish(topic="foobar", message={...})

Note that when I call a remote procedure there is no reference to the service that provides it - and this is different to core nameko where a service name must be provided. This simpler behaviour is explained by the Router Peer which maintains all the registrations and subscriptions on behalf of WAMP clients implementing these Roles.


Run Tests
---------

::

    $ pip install --editable .[dev]
    $ py.test ./test -vs


.. _wampy: https://github.com/noisyboiler/wampy
.. _nameko: https://github.com/nameko/nameko
