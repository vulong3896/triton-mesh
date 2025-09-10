from celery import shared_task
from orchestrator.models import Model, ModelInstance, TritonServer
from orchestrator.constants import (
    BEST_FIT, LEAST_LOADED, BIGGEST_FREE_MEMORY, 
    INSTANCE_LOADING, INSTANCE_READY, INSTANCE_ERROR,
    MODEL_DEPLOYED
)
from orchestrator.deploying import (
    BestFitStrategy, 
    LeastLoadedStrategy, 
    BiggestFreeMemoryStrategy
)
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
    server = instance.server

    # Set status to LOADING
    instance.status = INSTANCE_LOADING
    instance.save(update_fields=['status'])

    # Use Triton gRPC client to load the model
    triton_url = server.grpc_url 
    model_name = model.name

    try:
        with grpcclient.InferenceServerClient(url=triton_url) as client:
            client.load_model(model_name=model_name)
            is_ready = client.is_model_ready(model_name)
            if is_ready:
                instance.status = INSTANCE_READY
                instance.error_message = None
            else:
                instance.status = INSTANCE_ERROR
                instance.error_message = f"Model {model_name} not ready after load."
    except InferenceServerException as e:
        instance.status = INSTANCE_ERROR
        instance.error_message = str(e)
    except Exception as e:
        instance.status = INSTANCE_ERROR
        instance.error_message = f"Unexpected error: {str(e)}"

    instance.save()


@shared_task
def deploy_model(model_id):
    """
    Deploys a model to selected servers based on the model's deployment strategy.
    """
    model = Model.objects.get(id=model_id)
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

    for i in range(model.instance_num):
        if i < len(selected_servers):
            server = selected_servers[i]
        else:
            server = None
        instance = ModelInstance.objects.create(
            model=model,
            server=server
        )
        if server:
            load_instance.delay(instance.id)