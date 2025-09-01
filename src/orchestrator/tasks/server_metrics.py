from celery import shared_task
from orchestrator.models import TritonServer
from orchestrator.utils.metrics import parse_metrics, fetch_metrics_text
from orchestrator.utils.validate import validate_http_url
from orchestrator.constants import SERVER_UNHEALTHY, SERVER_HEALTHY
from .base import BaseTask

@shared_task(bind=True, base=BaseTask)
def craw_server_metrics(self):
    servers = TritonServer.objects.all()
    for server in servers:
        # Check liveness
        check_health_url = f"{server.http_url}/v2/health/live"
        error_message = validate_http_url(check_health_url)
        update_fields = []
        if error_message:
            server.status = SERVER_UNHEALTHY
            update_fields.append('status')
        else:
            url = f"{server.metrics_url}/metrics" 
            txt = fetch_metrics_text(url)
            metrics = parse_metrics(txt)
            for metric_name, metric_value in metrics.items():
                if metric_name == 'nv_cpu_memory_total_bytes':
                    server.total_cpu_memory_mb = metric_value / (1024 * 1024)
                    update_fields.append('total_cpu_memory_mb')
                if metric_name == 'nv_cpu_memory_used_bytes':
                    server.total_used_cpu_memory_mb = metric_value / (1024 * 1024)
                    update_fields.append('total_used_cpu_memory_mb')
                if metric_name == 'nv_gpu_memory_total_bytes':
                    server.total_gpu_memory_mb = metric_value / (1024 * 1024)
                    update_fields.append('total_gpu_memory_mb')
                if metric_name == 'nv_gpu_memory_used_bytes':
                    server.total_used_gpu_memory_mb = metric_value / (1024 * 1024)
                    update_fields.append('total_used_gpu_memory_mb')
        if update_fields: 
            server.save(update_fields=update_fields)
