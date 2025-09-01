

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from orchestrator.models import Model, ModelVersion
from orchestrator.serializers import ModelSerializer, ModelVersionSerializer
from django.shortcuts import get_object_or_404
from orchestrator.constants import MODEL_ARCHIVED, MODEL_DEPLOYED, MODEL_DRAFT
from orchestrator.errors import CANT_DELETE_NON_ARCHIVED_MODEL, MODEL_ALREADY_DEPLOYED


class ModelViewSet(viewsets.ViewSet):
    permission_classes = []

    def list(self, request):
        """
        List all models.
        """
        models = Model.objects.all()
        serializer = ModelSerializer(models, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieve a single model by id.
        """
        model = get_object_or_404(Model, pk=pk)
        serializer = ModelSerializer(model)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new model.
        """
        serializer = ModelSerializer(data=request.data)
        if serializer.is_valid():
            model = serializer.save()
            ModelVersion.objects.create(
                model=model
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Update an existing model.
        """
        model = get_object_or_404(Model, pk=pk)
        serializer = ModelSerializer(model, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a model.
        """
        model = get_object_or_404(Model, pk=pk)
        if model.status != MODEL_ARCHIVED:
            response = {
                'error_code': CANT_DELETE_NON_ARCHIVED_MODEL,
                'message': 'Cant delete non archived model, archive it first!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        model = get_object_or_404(Model, pk=pk)
        versions = ModelVersion.objects.filter(model=model)
        serializer = ModelVersionSerializer(versions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def version(self, request, pk=None):
        """
        Add a new version to the model.
        """
        serializer = ModelVersionSerializer(data=request.data)
        if serializer.is_valid():
            version = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)