from celery import shared_task
from orchestrator.models import Model, ModelVersion, ModelInstance, TritonServer
from orchestrator.constants import (
    BEST_FIT, LEAST_LOADED, BIGGEST_FREE_MEMORY, 
    MODEL_LOADING, MODEL_READY, MODEL_ERROR
)
from orchestrator.routing.deploy.best_fit import BestFitStrategy
from orchestrator.routing.deploy.least_loaded import LeastLoadedStrategy
from orchestrator.routing.deploy.biggest_free import BiggestFreeMemoryStrategy

import tritonclient.grpc as grpcclient
from tritonclient.utils import InferenceServerException

@shared_task
def load_instance(instance_id):
    """
    Task to load a model instance onto a specific server using TritonClient API.
    This function will communicate with the Triton server to load the model.
    """
    instance = ModelInstance.objects.get(id=instance_id)
    model = instance.model
    version = instance.version
    server = instance.server

    # Set status to LOADING
    instance.status = MODEL_LOADING
    instance.save(update_fields=['status'])

    # Use Triton gRPC client to load the model
    triton_url = server.grpc_url 
    model_name = model.name
    model_version = version.name

    try:
        with grpcclient.InferenceServerClient(url=triton_url) as client:
            # Load the model (Triton will load the latest version if version is not specified)
            client.load_model(model_name=model_name, model_version=model_version)
            # Optionally, you can check if the model is ready
            is_ready = client.is_model_ready(model_name, model_version=model_version)
            if is_ready:
                instance.status = MODEL_READY
                instance.error_message = None
            else:
                instance.status = MODEL_ERROR
                instance.error_message = f"Model {model_name} not ready after load."
    except InferenceServerException as e:
        instance.status = MODEL_ERROR
        instance.error_message = str(e)
    except Exception as e:
        instance.status = MODEL_ERROR
        instance.error_message = f"Unexpected error: {str(e)}"

    instance.save()


@shared_task
def deploy_model(version_id):
    """
    Deploys a model version to selected servers based on the model's deployment strategy.
    """
    version = ModelVersion.objects.get(id=version_id)
    model = version.model
    model.status = MODEL_DEPLOYED
    model.save(update_fields=['status'])

    # Select deployment strategy
    if model.deploy_algorithm == BEST_FIT:
        strategy = BestFitStrategy(model.id)
    elif model.deploy_algorithm == LEAST_LOADED:
        strategy = LeastLoadedStrategy(model.id)
    elif model.deploy_algorithm == BIGGEST_FREE_MEMORY:
        strategy = BiggestFreeMemoryStrategy(model.id)
    else:
        # Default to least loaded
        strategy = LeastLoadedStrategy(model.id)

    # Select servers for deployment
    selected_servers = strategy.select_servers()

    # Deploy model version to selected servers
    for server in selected_servers:
        # Check if already deployed
        exists = ModelInstance.objects.filter(
            model=model, version=version, server=server
        ).exists()
        if not exists:
            instance = ModelInstance.objects.create(
                model=model,
                version=version,
                server=server
            )
            load_instance.delay(instance.id)