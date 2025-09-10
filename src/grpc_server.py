import grpc
from concurrent import futures
import grpc_service_pb2
import grpc_service_pb2_grpc
from interceptor import GRPCMeshInterceptor


class GRPCInferenceServiceServicer(grpc_service_pb2_grpc.GRPCInferenceServiceServicer):
   
    def ModelInfer(self, request, context):
        print(request.model_name)
        return grpc_service_pb2.ModelInferResponse(message=f"Hello, {request.model_name}!")

    def ServerReady(self, request, context):
        return grpc_service_pb2.ServerReadyResponse(ready=True)

    def ServerLive(self, request, context):
        return grpc_service_pb2.ServerLiveResponse(live=True)

def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[GRPCMeshInterceptor(grpc_service_pb2_grpc.GRPCInferenceServiceStub)]
    )
    grpc_service_pb2_grpc.add_GRPCInferenceServiceServicer_to_server(GRPCInferenceServiceServicer(), server)
    server.add_insecure_port('[::]:8011')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()