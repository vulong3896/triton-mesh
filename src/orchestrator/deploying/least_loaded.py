from .interface import IDeployStrategy
from orchestrator.constants import CPU, GPU

class LeastLoadedStrategy(IDeployStrategy):
    """
    LeastLoadedStrategy selects servers for deployment based on the least used memory (CPU or GPU).
    """

    def select_servers(self):
        """
        Select servers for deploying the given model using the least loaded strategy.

        Returns:
            A list of selected server instances for deployment.
        """
        if len(self.candidate_servers) == 0:
            return []

        def used_gpu_mem(server):
            return server.total_used_gpu_memory_mb or 0

        def used_cpu_mem(server):
            return server.total_used_cpu_memory_mb or 0

        # Sort servers by used memory ascending (least used first)
        if self.model.type == GPU:
            sorted_servers = sorted(self.candidate_servers, key=used_gpu_mem)
        else:
            sorted_servers = sorted(self.candidate_servers, key=used_cpu_mem)

        num_instances = self.model.instance_num
        selected_servers = sorted_servers[:num_instances]

        return selected_servers
