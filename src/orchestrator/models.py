import uuid
from django.db import models
from .constants import (
    INSTANCE_LOADING, INSTANCE_READY, INSTANCE_ERROR,
    SERVER_HEALTHY, SERVER_UNHEALTHY, SERVER_INIT, INSTANCE_INIT,
    BEST_FIT, LEAST_LOADED, BIGGEST_FREE_MEMORY,
    ROUND_ROBIN, LEAST_SERVING, RANDOM, WEIGHTED_ROUND_ROBIN,
    MODEL_DRAFT, MODEL_DEPLOYED, MODEL_ARCHIVED,
    VERSION_NOT_LOADED, VERSION_DEPLOYED, VERSION_ARCHIVED,
    CPU, GPU
)
from django.core.validators import URLValidator
from django.core.validators import RegexValidator


class TritonServer(models.Model):
    STATUS_CHOICES = [
        (SERVER_HEALTHY, 'Healthy'),
        (SERVER_UNHEALTHY, 'Unhealthy'),
        (SERVER_INIT, "Init")
    ]
    TYPES = [
        (CPU, 'CPU'),
        (GPU, 'GPU')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    http_url = models.TextField(default='http://localhost:8000', validators=[URLValidator()])
    grpc_url = models.CharField(
        max_length=255,
        default='localhost:8001',
        validators=[
            RegexValidator(
                regex=r'^[\w\.-]+:\d+$',
                message='Enter a valid host:port (e.g., 127.0.0.1:8001 or myhost:8001)'
            )
        ]
    )
    metrics_url = models.TextField(default='http://localhost:8002', validators=[URLValidator()])
    type = models.CharField(max_length=16, choices=TYPES, default=GPU)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=SERVER_INIT)
    total_gpu_memory_mb = models.IntegerField(null=True, blank=True)
    total_used_gpu_memory_mb = models.IntegerField(null=True, blank=True)
    total_cpu_memory_mb = models.IntegerField(null=True, blank=True)
    total_used_cpu_memory_mb = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(null=True, blank=True)

    tags = models.ManyToManyField('Tag', related_name='servers', blank=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(primary_key=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
   
    def __str__(self):
        return self.name

class Model(models.Model):
    DEPLOY_ALGORITHMS = [
        (BEST_FIT, "Best fit"),
        (LEAST_LOADED, "Least loaded"),
        (BIGGEST_FREE_MEMORY, "Biggest free memory")
    ]
    ROUTING_ALGORITHMS = [
        (ROUND_ROBIN, "Round robin"), 
        (LEAST_SERVING, "Least serving"), 
        (RANDOM, "Random"), 
        (WEIGHTED_ROUND_ROBIN, "Weighted round robin")
    ]
    STATUSES = [
        (MODEL_DRAFT, "DRAFT"),
        (MODEL_DEPLOYED, "DEPLOYED"),
        (MODEL_ARCHIVED, "ARCHIVED")
    ]
    TYPES = [
        (CPU, 'CPU'),
        (GPU, 'GPU')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=16, choices=TYPES, default=GPU)
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUSES, default=MODEL_DRAFT)
    deploy_algorithm = models.CharField(max_length=50, choices=DEPLOY_ALGORITHMS, default=LEAST_LOADED)
    routing_algorithm = models.CharField(max_length=50, choices=ROUTING_ALGORITHMS, default=ROUND_ROBIN)
    instance_num = models.IntegerField(default=1)
    config = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    tags = models.ManyToManyField('Tag', related_name='models', blank=True)

    def __str__(self):
        return self.name

class ModelInstance(models.Model):
    STATUS_CHOICES = [
        (INSTANCE_LOADING, 'Loading'),
        (INSTANCE_READY, 'Ready'),
        (INSTANCE_ERROR, 'Error'),
        (INSTANCE_INIT, "Init")
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='instances')
    server = models.ForeignKey(TritonServer, on_delete=models.CASCADE, related_name='instances', null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=INSTANCE_INIT)
    loaded_at = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(null=True, blank=True)

    # class Meta:
    #     unique_together = ('model', 'version', 'server')

    def __str__(self):
        return f"Deployment of {self.model} on {self.server}"

class ModelMetric(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deployment = models.ForeignKey(ModelInstance, on_delete=models.CASCADE, related_name='metrics')
    timestamp = models.DateTimeField()
    infer_count = models.IntegerField()
    avg_latency_ms = models.FloatField()
    gpu_mem_used_mb = models.IntegerField()

    def __str__(self):
        return f"Metrics for {self.deployment} at {self.timestamp}"