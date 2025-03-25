from ..base import SolverAlgorithm
import random
import time
from typing import List, Tuple
import concurrent.futures
import copy

class GeneticAlgorithm(SolverAlgorithm):
    def __init__(self, cube, population_size=100, generations=50):
        super().__init__(cube)
        self.population_size = population_size
        self.generations = generations
        self.moves = ['F', 'B', 'L', 'R', 'U', 'D']

    @property
    def complexity(self):
        return f"O(g*p*e), g={self.generations}, p={self.population_size}"

    @property
    def description(self):
        return """Genetic Algorithm evolves a population of move sequences,
        using mutation and crossover to find better solutions."""

    def solve(self, progress_callback=None):
        # Lưu callback để cập nhật tiến trình
        if progress_callback:
            self.set_progress_callback(progress_callback)
            
        start_time = time.time()
        
        # Use parallel solver if available
        if self.parallel_solver:
            return self._parallel_solve(start_time)
            
        population = self._init_population()
        
        for generation in range(self.generations):
            if self.update_state_count():
                if self.states_explored >= self.max_states:
                    return []
                    
            population = sorted(population, 
                             key=lambda x: self._fitness(x[0]),
                             reverse=True)
            
            if self._fitness(population[0][0]) == 1.0:
                self.time_taken = time.time() - start_time
                self.solution = population[0][1]
                return population[0][1]
            
            new_population = population[:2]  # Keep best 2
            
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(population[:50], 2)
                child = self._crossover(parent1[1], parent2[1])
                child = self._mutate(child)
                new_cube = self._apply_sequence(self.cube, child)
                new_population.append((new_cube, child))
                
            population = new_population
            
        return []

    def _parallel_solve(self, start_time):
        """Genetic algorithm with parallel fitness evaluation"""
        population = self._init_population()
        
        for generation in range(self.generations):
            if self.update_state_count():
                if self.states_explored >= self.max_states:
                    return []
            
            # Evaluate fitness in parallel
            for cube, seq in population:
                self.parallel_solver.submit(self._fitness, cube)
            
            # Collect fitness results
            fitness_values = []
            for _ in range(len(population)):
                fitness = self.parallel_solver.get_result(timeout=0.1)
                if fitness is not None:
                    fitness_values.append(fitness)
            
            # Sort population by fitness
            population_with_fitness = list(zip(fitness_values, population))
            population_with_fitness.sort(reverse=True)
            
            # Check if we found a solution
            if population_with_fitness and population_with_fitness[0][0] == 1.0:
                self.time_taken = time.time() - start_time
                self.solution = population_with_fitness[0][1][1]  # [1] is population tuple, [1] is sequence
                return self.solution
            
            # Create new population
            new_population = [p[1] for p in population_with_fitness[:2]]  # Keep best 2
            
            # Generate new individuals in parallel
            tasks_submitted = 0
            while len(new_population) < self.population_size:
                # Select parents
                parent1, parent2 = random.sample([p[1] for p in population_with_fitness[:50]], 2)
                
                # Submit crossover and mutation task
                self.parallel_solver.submit(self._create_offspring, parent1, parent2)
                tasks_submitted += 1
            
            # Collect offspring
            for _ in range(tasks_submitted):
                offspring = self.parallel_solver.get_result(timeout=0.1)
                if offspring is not None:
                    new_population.append(offspring)
                    if len(new_population) >= self.population_size:
                        break
            
            population = new_population[:self.population_size]  # Ensure population size
        
        return []
    
    def _create_offspring(self, parent1, parent2):
        """Create offspring by crossover and mutation"""
        child_seq = self._crossover(parent1[1], parent2[1])
        child_seq = self._mutate(child_seq)
        new_cube = self._apply_sequence(self.cube, child_seq)
        return (new_cube, child_seq)

    def parallelize(self, executor, should_cancel):
        """Revert to single-threaded implementation due to pickling issues"""
        self.should_cancel = should_cancel
        start_time = time.time()
        solution = self.solve()
        self.time_taken = time.time() - start_time
        return solution

    def _create_child(self, seq1, seq2):
        """Create a child in parallel"""
        child = self._crossover(seq1, seq2)
        child = self._mutate(child)
        new_cube = self._apply_sequence(self.cube, child)
        return (new_cube, child)

    def _init_population(self) -> List[Tuple]:
        population = []
        for _ in range(self.population_size):
            sequence = [random.choice(self.moves) for _ in range(20)]
            new_cube = self._apply_sequence(self.cube, sequence)
            population.append((new_cube, sequence))
        return population

    def _fitness(self, cube) -> float:
        """Calculate how close the cube is to being solved"""
        # Sử dụng heuristic từ base class
        return 1.0 - self._heuristic(cube)  # Đảo ngược để 1 là tốt nhất, 0 là tệ nhất

    def _crossover(self, seq1: List, seq2: List) -> List:
        point = random.randint(0, len(seq1))
        return seq1[:point] + seq2[point:]

    def _mutate(self, sequence: List, rate=0.1) -> List:
        return [random.choice(self.moves) if random.random() < rate else move 
                for move in sequence]
