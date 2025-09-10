from rest_framework import serializers
from .models import Model, TritonServer, ModelInstance


class ModelSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    routing_algorithm_display = serializers.CharField(source='get_routing_algorithm_display', read_only=True)
    deploy_algorithm_display = serializers.CharField(source='get_deploy_algorithm_display', read_only=True)

    class Meta:
        model = Model
        fields = [
            'id', 'name', 'description', 
            "status", 'status_display',
            "instance_num", "type",
            'deploy_algorithm', 'deploy_algorithm_display',
            'routing_algorithm', 'routing_algorithm_display',
            'created_at', "last_update"
        ]
        read_only_fields = ['created_at', 'last_update']

class TritonServerSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TritonServer
        fields = [
            'id', 'name', 'status', 'status_display',
            'http_url', 'grpc_url', 'metrics_url', "type",
            'total_gpu_memory_mb', 'total_used_gpu_memory_mb',
            'total_cpu_memory_mb', 'total_used_cpu_memory_mb',
            'created_at', 'last_update', 'metadata', 'tags'
        ]
        read_only_fields = ['created_at', 'last_update']

class ModelInstanceFromTritonViewSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    model_id = serializers.UUIDField(source='model.id', read_only=True)
    model_name = serializers.CharField(source='model.name', read_only=True)

    class Meta:
        model = ModelInstance
        fields = [
            'id',
            'model_id',
            'model_name',
            'status', 'status_display',
            'error_message',
            'loaded_at'
        ]
        read_only_fields = ['loaded_at', 'error_message', 'model_id', 'model_name']

class ModelInstanceFromModelViewSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    server_id = serializers.UUIDField(source='server.id', read_only=True)
    server_name = serializers.CharField(source='server.name', read_only=True)

    class Meta:
        model = ModelInstance
        fields = [
            'id',
            'server_id',
            'server_name',
            'status', 'status_display',
            'error_message',
            'loaded_at'
        ]
        read_only_fields = ['loaded_at', 'error_message', 'server_id', 'server_name']
