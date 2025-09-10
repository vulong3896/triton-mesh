

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from orchestrator.models import Model, ModelInstance
from orchestrator.serializers import ModelSerializer
from django.shortcuts import get_object_or_404
from orchestrator.constants import MODEL_ARCHIVED, MODEL_DEPLOYED, MODEL_DRAFT
from orchestrator.errors import CANT_DELETE_DEPLOYED_MODEL, MODEL_ALREADY_DEPLOYED
from orchestrator.tasks import deploy_model, unload_model


class ModelViewSet(viewsets.ModelViewSet):
    permission_classes = []

    def list(self, request):
        """
        List all models with pagination, allowing page size from request.
        """
        queryset = Model.objects.all()
        page_size = request.query_params.get('page_size')
        if page_size:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        serializer = ModelSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

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
        if request.data.get('id', None):
            model = get_object_or_404(Model, pk=request.data['id'])
            serializer = ModelSerializer(model, data=request.data, partial=False)
        else:
            serializer = ModelSerializer(data=request.data)
            
        if serializer.is_valid():
            model = serializer.save()
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
        if model.status == MODEL_DEPLOYED:
            response = {
                'error_code': CANT_DELETE_DEPLOYED_MODEL,
                'message': 'Cant delete deployed model, archive it first!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        model = get_object_or_404(Model, pk=pk)
        model.status = MODEL_ARCHIVED
        model.save(update_fields=['status'])
        unload_model.delay(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def deploy(self, request, pk=None):
        model = get_object_or_404(Model, pk=pk)
        deploy_model.delay(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def unload(self, request, pk=None):
        model = get_object_or_404(Model, pk=pk)
        unload_model.delay(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)