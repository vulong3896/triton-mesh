from rest_framework import serializers
from .models import Model, TritonServer


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