from .interface import IDeployStrategy
from orchestrator.constants import CPU, GPU


class BiggestFreeMemoryStrategy(IDeployStrategy):
    """
    BestFitStrategy selects servers for deployment based on the "best fit" criteria.
    For demonstration, this implementation selects servers with the most available GPU memory.
    """
    
    def select_servers(self):
        """
        Select servers for deploying the given model using the best fit strategy.

        Args:
            model: The model instance to be deployed.
            candidate_servers: A queryset or list of available TritonServer instances.

        Returns:
            A list of selected server instances for deployment.
        """
        # Example: select the server(s) with the most available GPU memory
        # (total_gpu_memory_mb - total_used_gpu_memory_mb)
        # If candidate_servers is a queryset, we can annotate and order by available memory
        # Otherwise, sort in Python
        if len(self.candidate_servers)==0:
            return []

        def available_gpu_mem(server):
            total = server.total_gpu_memory_mb or 0
            used = server.total_used_gpu_memory_mb or 0
            return total - used
        
        def available_cpu_mem(server):
            total = server.total_cpu_memory_mb or 0
            used = server.total_used_cpu_memory_mb or 0
            return total - used

        # Sort servers by available CPU/GPU memory descending
        if self.model.type == GPU:
            sorted_servers = sorted(self.candidate_servers, key=available_gpu_mem, reverse=True)
        else:
            sorted_servers = sorted(self.candidate_servers, key=available_cpu_mem, reverse=True)

        # Select as many servers as needed for the model's instance_num
        num_instances = model.instance_num
        selected_servers = sorted_servers[:num_instances]

        return selected_servers
