from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from orchestrator.models import ModelVersion
from orchestrator.serializers import ModelVersionSerializer
from rest_framework.decorators import action
from orchestrator.tasks import deploy_model


class ModelVersionViewSet(viewsets.ViewSet):
    permission_classes = []

    def update(self, request, pk=None):
        """
        Update an existing model version.
        """
        version = get_object_or_404(ModelVersion, pk=pk)
        serializer = ModelVersionSerializer(version, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a model version.
        """
        version = get_object_or_404(ModelVersion, pk=pk)
        version.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def deploy(self, request, pk=None):
        version = get_object_or_404(ModelVersion, pk=pk)
        deploy_model.delay(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    
