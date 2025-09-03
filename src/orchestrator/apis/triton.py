from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import permissions
from orchestrator.models import TritonServer
from orchestrator.serializers import TritonServerSerializer
from django.shortcuts import get_object_or_404
from orchestrator.errors import TRITON_METRICS_URL_NOT_VALID, TRITON_HTTP_URL_NOT_VALID, TRITON_GRPC_URL_NOT_VALID
import tritonclient.grpc as grpcclient
from tritonclient.utils import InferenceServerException
import requests
from orchestrator.utils.validate import validate_http_url
from rest_framework.decorators import action


class TritonServerViewSet(viewsets.ViewSet):
    permission_classes = []

    def list(self, request):
        """
        List all Triton servers.
        """
        servers = TritonServer.objects.all()
        serializer = TritonServerSerializer(servers, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieve a single Triton server by id.
        """
        server = get_object_or_404(TritonServer, pk=pk)
        serializer = TritonServerSerializer(server)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new Triton server.
        """
        errors = {}
        http_url = request.data['http_url']
        check_health_url = f"{http_url}/v2/health/live"
        error_message = validate_http_url(check_health_url)
        if error_message:
            errors['http_url'] = [error_message]
            
        metrics_url = request.data['metrics_url']
        check_metrics_url = f"{metrics_url}/metrics"
        error_message = validate_http_url(check_metrics_url)
        if error_message:
            errors['metrics_url'] = [error_message]
        
        grpc_url = request.data['grpc_url']
        client = grpcclient.InferenceServerClient(url=grpc_url)
        try:
            if not client.is_server_live():
                errors['grpc_url'] = [
                    f'{grpc_url} is not live'
                ]
            if not client.is_server_ready():
                errors['grpc_url'] = [
                    f'{grpc_url} is not ready'
                ]
        except InferenceServerException as e:
            errors['grpc_url'] = [
                str(e)
            ]

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get('id', None):
            server = get_object_or_404(TritonServer, pk=request.data['id'])
            serializer = TritonServerSerializer(server, data=request.data, partial=False)
        else:
            serializer = TritonServerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Update an existing Triton server.
        """
        server = get_object_or_404(TritonServer, pk=pk)
        serializer = TritonServerSerializer(server, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a Triton server.
        """
        server = get_object_or_404(TritonServer, pk=pk)
        server.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
