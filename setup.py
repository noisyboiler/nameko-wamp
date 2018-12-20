from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))


# Get the long description from the README file
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()


setup(
    name='nameko-wamp',
    version='0.2.0',
    description='WAMP extension for nameko',
    long_description=long_description,
    url='https://github.com/noisyboiler/nameko_wamp',
    author='Simon Harrison',
    author_email='noisyboiler@googlemail.com',
    license='GNU GPLv3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='WAMP RPC',
    packages=find_packages(),
    install_requires=[
        "eventlet==0.21.0",
        "nameko==2.5.4",
        "six==1.10.0",
        "wampy==0.9.17",
    ],
    extras_require={
        'dev': [
            "crossbar==0.15.0",
            "autobahn==0.17.2",
            "Twisted==17.9.0",
            "pytest==3.1.3",
            "mock==1.3.0",
            "pytest==2.9.1",
            "pytest-capturelog==0.7",
            "colorlog",
            "flake8==3.5.0",
            "gevent-websocket==0.10.1",
            "coverage>=3.7.1",
            "Twisted==17.9.0",
        ]
    },
    entry_points={},
)
