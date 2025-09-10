# redirect_by_model.py
import grpc
from utils.registry import BackendRegistry
from collections import namedtuple
from grpc_interceptor import ServerInterceptor
from grpc_interceptor.exceptions import GrpcException
from typing import Callable, Any



class GRPCMeshInterceptor(ServerInterceptor):
    """
    Interceptor that forwards calls to upstream selected by request.model_name.
    `registry` is a BackendRegistry instance.
    """

    def __init__(self, stub_class, channel_options=None):
        self.registry = BackendRegistry('grpc')
        self.stub_class = stub_class
        self._channel_cache = {}
        self.channel_options = channel_options or []

    def _make_channel_and_stub(self, address):
        # reuse channel if exists
        if address in self._channel_cache:
            return self._channel_cache[address]
        chan = grpc.insecure_channel(address, options=self.channel_options)
        stub = self.stub_class(chan)
        self._channel_cache[address] = stub
        return stub

    def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: grpc.ServicerContext,
        method_name: str,
    ):
        if method_name == '/inference.GRPCInferenceService/ModelInfer':
            model_name = request_or_iterator.model_name
            address = self.registry.pick_backend(model_name)
            stub = self._make_channel_and_stub(address)
            response = stub.ModelInfer(request_or_iterator)
            return response
        else:
            return method(request_or_iterator, context)