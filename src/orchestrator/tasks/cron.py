from celery import shared_task
from orchestrator.models import ModelInstance, Model
from orchestrator.tasks.deploy import load_instance
from orchestrator.routing.deploy import (
    BestFitStrategy, 
    LeastLoadedStrategy, 
    BiggestFreeMemoryStrategy
)
from orchestrator.constants import (
    BEST_FIT, LEAST_LOADED, BIGGEST_FREE_MEMORY, 
    INSTANCE_READY, INSTANCE_ERROR, INSTANCE_INIT, 
)
import tritonclient.grpc as grpcclient
from tritonclient.utils import InferenceServerException
import logging


logger = logging.getLogger('mesh')


@shared_task
def assign_servers_to_unassigned_instances():
    """
    Query all ModelInstance objects with server=None, use the model's deployment strategy
    to find an appropriate server, assign it, and call load_instance if a server is found.
    """
    unassigned_instances = ModelInstance.objects.filter(server=None)
    for instance in unassigned_instances:
        model = instance.model
        # Select deployment strategy
        if model.deploy_algorithm == BEST_FIT:
            strategy = BestFitStrategy(model.id)
        elif model.deploy_algorithm == LEAST_LOADED:
            strategy = LeastLoadedStrategy(model.id)
        elif model.deploy_algorithm == BIGGEST_FREE_MEMORY:
            strategy = BiggestFreeMemoryStrategy(model.id)
        else:
            strategy = LeastLoadedStrategy(model.id)
        # Select servers for deployment
        selected_servers = strategy.select_servers()
        logger.debug(f"Found {len(selected_servers)} servers: {selected_servers} for {instance} with strategy {strategy}")
        if selected_servers:
            server = selected_servers[0]
            instance.server = server
            instance.save(update_fields=["server"])
            load_instance.delay(instance.id)

@shared_task
def reload_errored_instances():
    """
    Periodic task to reload all model instances that are in MODEL_ERROR status.
    """
    errored_instances = ModelInstance.objects.filter(status=INSTANCE_ERROR)
    for instance in errored_instances:
        server = instance.server
        model = instance.model
        version = instance.version
        if not server:
            continue  # Can't reload if no server assigned

        triton_url = server.grpc_url
        model_name = model.name
        model_version = str(version.name)

        try:
            with grpcclient.InferenceServerClient(url=triton_url) as client:
                # Check if server is live/ready
                if client.is_server_live() and client.is_server_ready():
                    # Check if model is ready
                    is_ready = client.is_model_ready(model_name, model_version=model_version)
                    if is_ready:
                        instance.status = INSTANCE_READY
                        instance.error_message = None
                        instance.save(update_fields=["status", "error_message"])
                    else:
                        # If instance is not ready, reload the instance
                        load_instance.delay(instance.id)
                else:
                    # Server is not ready, try to find a new server
                    # Select deployment strategy
                    if model.deploy_algorithm == BEST_FIT:
                        strategy = BestFitStrategy(model.id)
                    elif model.deploy_algorithm == LEAST_LOADED:
                        strategy = LeastLoadedStrategy(model.id)
                    elif model.deploy_algorithm == BIGGEST_FREE_MEMORY:
                        strategy = BiggestFreeMemoryStrategy(model.id)
                    else:
                        strategy = LeastLoadedStrategy(model.id)
                    selected_servers = strategy.select_servers()
                    # Exclude the current server
                    selected_servers = [s for s in selected_servers if s != server]
                    if selected_servers:
                        new_server = selected_servers[0]
                        instance.server = new_server
                        instance.save(update_fields=["server"])
                        load_instance.delay(instance.id)
                    else:
                        # No available server found, optionally log or set error
                        instance.error_message = "No available healthy server found for redeployment."
                        instance.save(update_fields=["error_message"])
        except InferenceServerException as e:
            instance.error_message = str(e)
            instance.save(update_fields=["error_message"])
        except Exception as e:
            instance.error_message = f"Unexpected error: {str(e)}"
            instance.save(update_fields=["error_message"])