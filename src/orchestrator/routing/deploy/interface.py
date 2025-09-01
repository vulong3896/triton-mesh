from abc import ABC, abstractmethod

from orchestrator.models import Model, TritonServer

class IDeployStrategy(ABC):

    def __init__(self, model_id):
        """
        Initialize the deployment strategy by querying model info and available servers
        with the same tag as the model's tags.
        """
        # Query the model instance
        self.model = Model.objects.get(id=model_id)
        # Get all tags associated with the model
        model_tags = self.model.tags.all()
        # Query available servers that have at least one tag in common with the model's tags
        self.candidate_servers = TritonServer.objects.filter(tags__in=model_tags, type=model.type).distinct()

    @abstractmethod
    def select_servers(self, model, candidate_servers):
        """
        Select servers for deploying the given model.

        Args:
            model: The model instance to be deployed.
            candidate_servers: A list of available server instances.

        Returns:
            A list of selected server instances for deployment.
        """
        pass
