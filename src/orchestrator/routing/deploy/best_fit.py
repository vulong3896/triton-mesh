from .interface import IDeployStrategy
from orchestrator.constants import CPU, GPU

class BestFitStrategy(IDeployStrategy):
    """
    BestFitStrategy selects servers for deployment based on the "best fit" criteria.
    This implementation selects servers whose available memory most closely matches the model's needs,
    minimizing wasted resources.
    """