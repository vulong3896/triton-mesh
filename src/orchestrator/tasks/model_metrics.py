from celery import shared_task
from orchestrator.models import ModelInstance
from orchestrator.constants import MODEL_READY
import tritonclient.grpc as grpcclient
from tritonclient.utils import InferenceServerException

from celery.schedules import crontab
from celery import Celery

app = Celery('orchestrator')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run every 5 minutes
    sender.add_periodic_task(
        crontab(minute='*/5'),
        check_all_instance_readiness.s(),
        name='check model instance readiness every 5 min'
    )

@shared_task
def check_all_instance_readiness():
    """
    Periodic task to check readiness of all model instances.
    """
    instances = ModelInstance.objects.all()
    for instance in instances:
        server = instance.server
        model = instance.model
        version = instance.version
        triton_url = server.grpc_url
        model_name = model.name
        model_version = str(version.name)
        try:
            with grpcclient.InferenceServerClient(url=triton_url) as client:
                is_ready = client.is_model_ready(model_name, model_version=model_version)
                if is_ready and instance.status != MODEL_READY:
                    instance.status = MODEL_READY
                    instance.error_message = None
                    instance.save(update_fields=['status', 'error_message'])
        except InferenceServerException as e:
            instance.error_message = str(e)
            instance.save(update_fields=['error_message'])
        except Exception as e:
            instance.error_message = f"Unexpected error: {str(e)}"
            instance.save(update_fields=['error_message'])