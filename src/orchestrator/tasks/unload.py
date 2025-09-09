from celery import shared_task
from orchestrator.models import ModelInstance
import tritonclient.grpc as grpcclient
from orchestrator.constants import (
    INSTANCE_READY, INSTANCE_ERROR, INSTANCE_INIT, 
    VERSION_DEPLOYED, VERSION_NOT_LOADED
)

@shared_task
def unload_instance(instance_id):
    """
    Unloads a specific model instance from its assigned Triton server.
    """
    try:
        instance = ModelInstance.objects.get(id=instance_id)
        server = instance.server
        model = instance.model

        if not server:
            instance.status = INSTANCE_ERROR
            instance.error_message = "No server assigned to this instance."
            instance.save(update_fields=["status", "error_message"])
            return

        with grpcclient.InferenceServerClient(url=server.grpc_url) as client:
            model_name = model.name

            try:
                client.unload_model(model_name)
                instance.status = INSTANCE_INIT
                instance.error_message = None
            except Exception as e:
                instance.status = INSTANCE_ERROR
                instance.error_message = f"Failed to unload: {str(e)}"
            instance.save(update_fields=["status", "error_message"])
    except ModelInstance.DoesNotExist:
        pass

@shared_task
def unload_model(model_id):
    """
    Unloads all instances of a model from their servers and updates instance status.
    """
    try:
        instances = ModelInstance.objects.filter(model_id=model_id)
        for instance in instances:
            unload_instance.delay(instance.id)
    except ModelVersion.DoesNotExist:
        pass
