from nameko.extensions import DependencyProvider
from wampy.roles.caller import RpcProxy

from . import WampClientProxy


class Caller(DependencyProvider):

    proxy = WampClientProxy()

    def get_dependency(self, worker_ctx):
        call_proxy = RpcProxy(client=self.proxy.client)
        return call_proxy
