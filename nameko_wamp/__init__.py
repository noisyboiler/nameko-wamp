import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


root = logging.getLogger(__name__)
root.addHandler(NullHandler())
