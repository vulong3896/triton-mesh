from celery import shared_task
from orchestrator.models import ModelInstance
from orchestrator.constants import (
    INSTANCE_READY, INSTANCE_ERROR
)
import tritonclient.grpc as grpcclient
from tritonclient.utils import InferenceServerException


@shared_task
def check_all_instance_readiness():
    """
    Periodic task to check readiness of all model instances.
    """
    instances = ModelInstance.objects.all()
    for instance in instances:
        server = instance.server
        if not server:
            continue
        model = instance.model
        triton_url = server.grpc_url
        model_name = model.name
        try:
            with grpcclient.InferenceServerClient(url=triton_url) as client:
                is_ready = client.is_model_ready(model_name)
                if is_ready and instance.status != INSTANCE_READY:
                    instance.status = INSTANCE_READY
                    instance.error_message = None
                    instance.save(update_fields=['status', 'error_message'])
        except InferenceServerException as e:
            instance.status = INSTANCE_ERROR
            instance.error_message = str(e)
            instance.save(update_fields=['status', 'error_message'])
        except Exception as e:
            instance.status = INSTANCE_ERROR
            instance.error_message = f"Unexpected error: {str(e)}"
            instance.save(update_fields=['status', 'error_message'])