from ..base import SolverAlgorithm
import math
import random
import time
from typing import Dict, List

class Node:
    def __init__(self, cube, parent=None, move=None):
        self.cube = cube
        self.parent = parent
        self.move = move
        self.children: Dict[str, Node] = {}
        self.visits = 0
        self.wins = 0

class MonteCarloTreeSearch(SolverAlgorithm):
    def __init__(self, cube, iterations=1000):
        super().__init__(cube)
        self.iterations = iterations
        self.moves = ['F', 'B', 'L', 'R', 'U', 'D']

    @property
    def complexity(self):
        return f"O(n*log(n)), n={self.iterations}"

    @property
    def description(self):
        return """Monte Carlo Tree Search explores moves by simulating random
        games and focusing on promising sequences."""

    def solve(self, progress_callback=None):
        # Lưu callback để cập nhật tiến trình
        if progress_callback:
            self.set_progress_callback(progress_callback)
            
        start_time = time.time()
        root = Node(self.cube)
        
        for i in range(self.iterations):
            # Cập nhật tiến trình
            if i % 10 == 0:
                self.update_progress(i, self.iterations)
                
            node = self._select(root)
            child = self._expand(node)
            result = self._simulate(child)
            self._backpropagate(child, result)
            
            if self._is_solved(node.cube):
                self.time_taken = time.time() - start_time
                self.solution = self._get_move_sequence(node)
                return self.solution
        
        return self._get_move_sequence(root)

    def _select(self, node: Node) -> Node:
        while node.children and not self._is_solved(node.cube):
            if len(node.children) < len(self.moves):
                return node
            node = self._get_best_uct(node)
        return node

    def _expand(self, node: Node) -> Node:
        if self._is_solved(node.cube):
            return node
            
        unused_moves = set(self.moves) - set(node.children.keys())
        if not unused_moves:
            return node
            
        move = random.choice(list(unused_moves))
        new_cube = self._apply_move(node.cube, move)
        child = Node(new_cube, node, move)
        node.children[move] = child
        return child

    def _simulate(self, node: Node, max_moves=20) -> bool:
        cube = node.cube
        for _ in range(max_moves):
            if self._is_solved(cube):
                return True
            move = random.choice(self.moves)
            cube = self._apply_move(cube, move)
        return False

    def _backpropagate(self, node: Node, result: bool):
        while node:
            node.visits += 1
            node.wins += result
            node = node.parent

    def _get_best_uct(self, node: Node) -> Node:
        C = math.sqrt(2)
        best_score = float('-inf')
        best_child = None
        
        for child in node.children.values():
            score = (child.wins / child.visits + 
                    C * math.sqrt(math.log(node.visits) / child.visits))
            if score > best_score:
                best_score = score
                best_child = child
                
        return best_child

    def _get_move_sequence(self, node: Node) -> List[str]:
        sequence = []
        while node.parent:
            sequence.append(node.move)
            node = node.parent
        return list(reversed(sequence))
