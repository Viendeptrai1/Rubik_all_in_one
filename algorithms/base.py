from abc import ABC, abstractmethod
from typing import List, Dict, Any

class RubikSolverAlgorithm(ABC):
    """Base class for all Rubik solving algorithms"""
    
    def __init__(self, cube):
        self.cube = cube
        self.solution: List[str] = []
        self.stats: Dict[str, Any] = {
            'nodes_explored': 0,
            'time_taken': 0,
            'solution_length': 0,
            'memory_used': 0
        }

    @abstractmethod
    def solve(self) -> List[str]:
        """Solve the cube and return list of moves"""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get algorithm statistics"""
        pass

    @abstractmethod
    def step(self) -> bool:
        """Perform one step of the algorithm. Returns True if solution is found"""
        pass
