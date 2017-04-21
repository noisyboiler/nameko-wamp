import eventlet
from wampy.errors import WampyError

from nameko_wamp.extensions import WampCalleeProxy, WampTopicProxy


def wait_for_registrations(container, number_of_registrations):
    if not container.started:
        raise WampyError(
            "Cannot look for registrations unless the service is running"
        )

    for ext in container.extensions:
        if type(ext) == WampCalleeProxy:
            break
    else:
        raise WampyError(
            "no clients found registering callees"
        )

    session = ext.client.session

    with eventlet.Timeout(5):
        while (
            len(session.registration_map.keys())
            < number_of_registrations
        ):
            eventlet.sleep()


def wait_for_subscriptions(container, number_of_subscriptions):
    if not container.started:
        raise WampyError(
            "Cannot look for registrations unless the service is running"
        )

    for ext in container.extensions:
        if type(ext) == WampTopicProxy:
            break
    else:
        raise WampyError(
            "no clients found subscribing to topics"
        )

    session = ext.client.session

    with eventlet.Timeout(5):
        while (
            len(session.subscription_map.keys())
            < number_of_subscriptions
        ):
            eventlet.sleep()
