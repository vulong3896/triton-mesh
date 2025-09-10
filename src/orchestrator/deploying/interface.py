from abc import ABC, abstractmethod
from orchestrator.constants import SERVER_HEALTHY
from orchestrator.models import Model, TritonServer

import logging


logger = logging.getLogger('mesh')

class IDeployStrategy(ABC):

    def __init__(self, model_id):
        """
        Initialize the deployment strategy by querying model info and available servers
        with the same tag as the model's tags.
        """
        self.model = Model.objects.get(id=model_id)
        params = {'type': self.model.type, 'status': SERVER_HEALTHY}
        model_tags = self.model.tags.all()
        if model_tags:
            params['tags__in'] = model_tags
        self.candidate_servers = TritonServer.objects.filter(**params).distinct()
        
        logger.debug(f"Candidate servers: {self.candidate_servers}")

    def __str__(self):
        return self.__class__.__name__

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
