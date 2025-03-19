import sys
import os
import time
import unittest

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rubik import RubikCube
from algorithms.advanced import KociembaAlgorithm, ThistlethwaiteAlgorithm

class TestAdvancedAlgorithms(unittest.TestCase):
    def test_kociemba_simple_scramble(self):
        """Test Kociemba's algorithm with a simple scramble"""
        cube = RubikCube()
        # Apply a simple scramble: R U R' U'
        cube.rotate_face('R', True)  # R
        cube._complete_rotation()    # Ensure rotation completes
        cube.rotate_face('U', True)  # U
        cube._complete_rotation()
        cube.rotate_face('R', False) # R'
        cube._complete_rotation()
        cube.rotate_face('U', False) # U'
        cube._complete_rotation()
        
        # Solve with Kociemba's algorithm
        solver = KociembaAlgorithm(cube, max_depth_phase1=10, max_depth_phase2=8)
        solution = solver.solve()
        
        self.assertIsNotNone(solution)
        self.assertTrue(len(solution) > 0)
        
        # Apply solution to scrambled cube
        for move in solution:
            cube.rotate_face(move[0], "'" not in move)
            cube._complete_rotation()
            
        # Verify cube is solved
        self.assertTrue(solver._is_solved(cube))
    
    def test_thistlethwaite_simple_scramble(self):
        """Test Thistlethwaite's algorithm with a simple scramble"""
        cube = RubikCube()
        # Apply a simple scramble: F R U B
        cube.rotate_face('F', True)
        cube._complete_rotation()
        cube.rotate_face('R', True)
        cube._complete_rotation()
        cube.rotate_face('U', True)
        cube._complete_rotation()
        cube.rotate_face('B', True)
        cube._complete_rotation()
        
        # Solve with Thistlethwaite's algorithm
        solver = ThistlethwaiteAlgorithm(cube)
        solution = solver.solve()
        
        self.assertIsNotNone(solution)
        self.assertTrue(len(solution) > 0)
        
        # Apply solution to scrambled cube
        for move in solution:
            cube.rotate_face(move[0], "'" not in move)
            cube._complete_rotation()
            
        # Verify cube is solved
        self.assertTrue(solver._is_solved(cube))

if __name__ == "__main__":
    unittest.main()
