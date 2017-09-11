import eventlet
import logging
from wampy.errors import WampyError

from nameko_wamp.extensions.dependencies import (
    WampCalleeProxy, WampTopicProxy)

logger = logging.getLogger(__name__)

TIMEOUT = 5


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

    success = False
    with eventlet.Timeout(TIMEOUT, False):
        while (
            len(session.registration_map.keys())
            < number_of_registrations
        ):
            eventlet.sleep()
        success = True

    if not success:
        logger.error(
            "%s has not registered %s callees",
            ext.client.name, number_of_registrations
        )
        raise WampyError(
            "Registrations Not Found: {}".format(
                session.registration_map.keys()
            )
        )

    logger.info("found registrations: %s", session.registration_map.keys())


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

    success = False
    with eventlet.Timeout(TIMEOUT, False):
        while (
            len(session.subscription_map.keys())
            < number_of_subscriptions
        ):
            eventlet.sleep()
        success = True

    if not success:
        logger.error(
            "%s has not subscribed to %s topics",
            ext.client.name, number_of_subscriptions
        )
        raise WampyError("Subscriptions Not Found")

    logger.info("found subscriptions: %s", session.subscription_map.keys())
