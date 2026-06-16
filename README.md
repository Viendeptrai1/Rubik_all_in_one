# 🧩 3D Rubik Simulator & Solver: An AI-Based Approach

## 1. Introduction

### 1.1. Problem Statement: Pathfinding in the State Space

Solving a Rubik's Cube represents a classic challenge in discrete state-space search. With an enormous state space ($> 4.3 \times 10^{19}$ states for the 3x3x3 cube and $3.7 \times 10^6$ states for the 2x2x2 cube), finding an optimal sequence of moves that transforms any scrambled configuration into the goal state is an NP-hard problem.

Mathematically, the Rubik's Cube state space can be represented as a graph $G=(V,E)$, where:
- $V$: the set of vertices representing all possible Rubik's Cube configurations
- $E$: the set of edges representing valid moves between configurations

The objective is to find the shortest path $P = \{v_0, v_1, ..., v_n\}$, where $v_0$ is the initial scrambled state and $v_n$ is the goal state (the solved cube).

### 1.2. Objectives and Requirements

The "3D Rubik Simulator & Solver" project aims to achieve the following objectives:

1. **Build a 3D simulation environment:**
   - Create an intuitive visual interface for 2x2x2 and 3x3x3 Rubik's Cubes
   - Support user interactions, including rotating, scrambling, and observing the solving process

2. **Implement a variety of AI search algorithms:**
   - **Group 1: Uninformed Search** - BFS, DFS, UCS, IDS
   - **Group 2: Informed Search** - A*, IDA*, Greedy Best-First Search
   - **Group 3: Local Search** - Hill Climbing (Simple, Random Restart, Stochastic), Simulated Annealing, Genetic Algorithm, Local Beam Search
   - **Group 4: Reinforcement Learning** - DeepCubeA (DQRN)
   - **Group 5: Constraint Satisfaction Problems (CSP)** - Backtracking, AC-3

3. **Evaluate and compare performance:**
   - Computation time $(T)$
   - Solution length $(L)$
   - Number of generated/explored states $(N)$
   - Memory usage $(M)$
   - Effective branching factor $b^* = \sqrt[d]{N}$, where $d$ is the solution depth

4. **Support educational purposes:**
   - Visualize AI algorithms using a practical example
   - Illustrate concepts related to state spaces, heuristics, and optimization techniques

### 1.3. Scope and Target Users

#### 1.3.1. Scope
- Simulate standard 2x2x2 and 3x3x3 Rubik's Cubes
- Implement basic-to-advanced AI search algorithms
- Develop a 3D graphical interface using PyOpenGL and PyQt5
- Use a Pattern Database (PDB) as a heuristic for the 2x2 cube

#### 1.3.2. Target Users
- Students and lecturers in Artificial Intelligence and Computer Science
- Developers interested in AI algorithms and combinatorial optimization
- Rubik's Cube enthusiasts who want to understand AI-based solving approaches

#### 1.3.3. Current Limitations
- The Pattern Database is currently implemented only at a basic level for the 2x2 cube
- DeepCubeA training is limited to a scrambling depth of 10 because of hardware constraints
- The system has not yet been fully optimized for complex cases with high scrambling depths

## 2. Theoretical Background

### 2.1. Programming Language and Development Tools

- **Primary language:** Python 3.13
  - Chosen for its flexibility and rich ecosystem of AI and graphics libraries
  - Supports functional, object-oriented, and procedural programming paradigms

- **IDE:** Visual Studio Code
  - Code completion through IntelliSense
  - Debugging and project-management support
  - Git integration

- **Operating systems:** Cross-platform support (Windows and macOS)
  - Ensures portability and compatibility

- **Source-code management:** Git and GitHub
  - Branching system for parallel development
  - Change-history tracking and code merging

### 2.2. Libraries Used

#### 2.2.1. Libraries for the User Interface and 3D Rubik's Cube Simulation
- **PyQt5**: A cross-platform GUI framework
  - `QMainWindow`, `QWidget`, and `QTabWidget` for interface structure
  - `QDockWidget` for flexible control panels
  - Signals and slots for event handling

- **PyOpenGL**: Python bindings for OpenGL
  - 3D rendering and the graphics pipeline
  - Matrix transformations for rotating and moving the Rubik's Cube
  - Shader programming for graphical effects

- **NumPy**: Array and matrix computation
  - Efficient storage and manipulation of multidimensional arrays
  - Spatial-coordinate transformations and rotations

#### 2.2.2. Libraries for Basic Search Algorithms
- **heapq**: Priority-queue implementation
  - $O(\log n)$ insertion and extraction operations
  - A core component of A*, UCS, and Greedy Best-First Search

- **collections.deque**: Double-ended queue
  - $O(1)$ insertion and removal at both ends
  - Efficient for BFS and ReplayBuffer implementations

- **random**: Random-number generation
  - Random Rubik's Cube scrambling
  - Stochastic algorithms such as Hill Climbing and Simulated Annealing

- **math**: Mathematical functions
  - $\exp()$ for Simulated Annealing
  - Evaluation functions and state-transition probabilities

- **pickle**: Serialization of Python objects
  - Saving and loading the ReplayBuffer
  - Preserving complex data structures between execution sessions

#### 2.2.3. Libraries for Reinforcement-Learning Models
- **PyTorch**: A deep-learning framework
  - Tensor API for parallel computation
  - `nn.Module` for building neural networks
  - `optim.Adam` and other optimization algorithms
  - CUDA support for GPU computation

### 2.3. Theoretical Foundations

#### 2.3.1. Rubik's Cube Group Theory
The Rubik's Cube can be modeled using mathematical group theory:

- **Definition of the Rubik's Cube group**: A group $G = (S, \circ)$, where $S$ is the set of all possible Rubik's Cube configurations and $\circ$ is the composition of rotations.

- **Group properties**:
  - *Closure*: Any sequence of rotations produces a valid Rubik's Cube configuration
  - *Associativity*: $(A \circ B) \circ C = A \circ (B \circ C)$, where $A$, $B$, and $C$ are rotations
  - *Identity element*: A rotation that leaves the configuration unchanged (a 0° rotation)
  - *Inverse element*: Every rotation has an inverse rotation in the opposite direction

- **State representation**:
  - 3x3x3 cube: 20 movable cubies (8 corners + 12 edges)
  - 2x2x2 cube: 8 corner cubies, each with 3 possible orientations

#### 2.3.2. State-Space Search Theory

The Rubik's Cube problem can be represented as a 4-tuple $(S, A, T, G)$, where:
- $S$: the set of states (Rubik's Cube configurations)
- $A$: the set of actions (basic rotations)
- $T: S \times A \rightarrow S$: the state-transition function
- $G \subset S$: the set of goal states (solved configurations)

**Uninformed search methods**:
- BFS: $O(b^d)$ time and space complexity
- DFS: $O(b^m)$ time complexity and $O(bm)$ space complexity
- UCS: $O(b^{C*/\epsilon})$, where $C*$ is the optimal solution cost

**Informed search methods**:
- Heuristic function $h(n)$: Estimates the distance from state $n$ to the goal state
- A*: $f(n) = g(n) + h(n)$, where $g(n)$ is the actual cost from the initial state to $n$
- Admissibility: $h(n) \leq h^*(n)$, where $h^*(n)$ is the true cost to the goal

**Pattern Database (PDB)**:
- Precomputes exact costs for a subset of cubies
- Formula: $h_{PDB}(s) = \max_{i \in \text{databases}} h_i(s)$

#### 2.3.3. Reinforcement-Learning Theory

The DeepCubeA model is based on a deep reinforcement-learning architecture:

- **Bellman equation**: $V^*(s) = \max_a [R(s,a) + \gamma \sum_{s'} P(s'|s,a)V^*(s')]$

- **Network architecture**: A deep neural network (DNN) with:
  - Input layer: One-hot encoding of the Rubik's Cube state
  - Hidden layers: Fully connected layers with ReLU activation
  - Output layer: State value $V(s)$

- **Learning method**:
  - Deep Q-learning with a ReplayBuffer
  - Weighted Approximate-Rank Pairwise (WARP) loss
  - $L_{WARP}(s_i, s_j) = \log(1 + \text{rank}_j) \cdot \max(0, m + V(s_j) - V(s_i))$
  where $s_i$ is closer to the goal than $s_j$, and $m$ is the margin

## 3. Solution Analysis and Design

### 3.1. Analysis of Uninformed Search Solutions

**Overall architecture**:
```text
┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
│ Rubik's Cube State │────▶│ Uninformed Search  │────▶│ Result             │
│ Model              │     │ Algorithm          │     │ Visualization      │
└────────────────────┘     └────────────────────┘     └────────────────────┘
```

**Breadth-First Search (BFS)**:
- **Data structure**: FIFO queue implemented with `collections.deque`
- **Complexity**: $O(b^d)$ time and space
- **Advantage**: Finds the shortest solution
- **Disadvantage**: Requires a large amount of memory and is impractical for the 3x3x3 cube

**Depth-First Search (DFS)**:
- **Data structure**: LIFO stack
- **Complexity**: $O(b^m)$ time and $O(bm)$ space
- **Advantage**: Requires less memory
- **Disadvantage**: May fail to find an optimal solution and can become trapped in an infinite path

**Iterative Deepening Search (IDS)**:
- **Strategy**: Repeatedly performs depth-limited DFS with an increasing depth limit
- **Complexity**: $O(b^d)$ time and $O(bd)$ space
- **Advantage**: Combines the benefits of BFS (shortest solution) and DFS (low memory usage)

**Uniform Cost Search (UCS)**:
- **Data structure**: Priority queue implemented with `heapq`
- **Priority criterion**: Actual path cost $g(n)$ from the initial state
- **Special use case**: Useful when different rotations have different costs

### 3.2. Analysis of Informed Search Solutions

**System architecture**:
```text
┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
│ Rubik's Cube Model │────▶│ Heuristic Function │────▶│ Informed Search    │────▶│ Result             │
│                    │     │                    │     │ Algorithm          │     │ Visualization      │
└────────────────────┘     └────────────────────┘     └────────────────────┘     └────────────────────┘
```

**Greedy Best-First Search**:
- **Strategy**: Always expands the node with the smallest heuristic value $h(n)$
- **Evaluation function**: $f(n) = h(n)$
- **Advantage**: Uses less time and memory than uninformed search algorithms
- **Disadvantage**: Does not guarantee an optimal solution

**A* Search**:
- **Strategy**: Combines the actual cost $g(n)$ with the heuristic value $h(n)$
- **Evaluation function**: $f(n) = g(n) + h(n)$
- **Properties**:
  - Complete: Always finds a solution if one exists
  - Optimal: If $h(n)$ is admissible ($h(n) \leq h^*(n)$)
- **Disadvantage**: High memory cost

**IDA* (Iterative Deepening A*)**:
- **Strategy**: Combines IDS with the A* evaluation function
- **Complexity**: $O(b^d)$ time and $O(bd)$ space
- **Advantage**: Uses less memory than A* while still finding an optimal solution

**Pattern Database (PDB)**:
- **Principle**: Precomputes and stores exact distances for a subset of cubies
- **Implementation for the 2x2x2 cube**:
  - Corner Pattern Database
  - Formula: $h_{PDB}(s) = \text{lookupTable}[\text{hashFunction}(s)]$

### 3.3. Analysis of the Reinforcement-Learning Solution

**DeepCubeA architecture**:
```text
┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
│ Rubik's Cube Model │────▶│ State-Evaluation   │────▶│ MCTS + Informed    │
│                    │     │ DNN                │     │ Search             │
└────────────────────┘     └────────────────────┘     └────────────────────┘
          │                          ▲                          │
          │                          │                          │
          ▼                          │                          ▼
┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
│ Training-Data      │────▶│ DNN Training       │◀────│ Solution-Result    │
│ Generation         │     │                    │     │ Evaluation         │
└────────────────────┘     └────────────────────┘     └────────────────────┘
```

**Neural-network design**:
- **Input**: One-hot encoded Rubik's Cube state (324 features for the 3x3x3 cube)
- **Architecture**: Fully connected network (4096-2048-1024-512-1)
- **Activation**: ReLU for hidden layers and no activation function for the output layer
- **Output**: Estimated distance to the goal state

**Training algorithm**:
1. Generate a dataset by applying reverse scrambles from the goal state
2. Iteratively update the state value $V(s)$ according to the Bellman equation
3. Use WARP loss to optimize the relative ordering of states
4. Apply Experience Replay to improve training stability

**Search algorithm**:
- Integrate the value predicted by the neural network into an informed search algorithm
- Evaluation function: $f(n) = g(n) + w \cdot V(n)$, where $w$ is a weighting coefficient
- Apply pruning based on the estimated cost

## 4. Experiments, Evaluation, and Result Analysis

### 4.1. Practical Evaluation Process

#### 4.1.1. Hardware Configuration
- **CPU**: Intel Core i9-11900K @ 3.5 GHz (8 cores, 16 threads)
- **RAM**: 32 GB DDR4 3200 MHz
- **GPU**: NVIDIA GeForce RTX 3080 (10 GB VRAM)
- **Storage**: 1 TB NVMe SSD

#### 4.1.2. DeepCubeA Model Configuration
- **Batch size**: 512
- **Learning rate**: 0.001
- **Optimizer**: Adam ($\beta_1=0.9$, $\beta_2=0.999$)
- **Epochs**: 1000
- **Replay Buffer size**: 10,000,000 transitions
- **Discount factor**: $\gamma = 0.99$
- **Maximum scrambling depth**: 10 (limited by hardware)

### 4.2. Algorithm Performance Statistics

#### 4.2.1. Uninformed Search Algorithms
| Algorithm | Rubik's Cube 2x2 (5 moves) | Rubik's Cube 2x2 (7 moves) | Rubik's Cube 3x3 (5 moves) |
|------------|-----------------------------|-----------------------------|-----------------------------|
| BFS | 0.5 s / 243 states | 10.2 s / 5,041 states | 125.7 s / 153,632 states |
| DFS | 0.3 s / 32 states* | 0.8 s / 64 states* | 1.2 s / 128 states* |
| IDS | 2.1 s / 315 states | 45.8 s / 6,224 states | 580.3 s / 187,450 states |
| UCS | 0.6 s / 251 states | 11.5 s / 5,214 states | 132.1 s / 158,745 states |

*: Non-optimal solution

#### 4.2.2. Informed Search Algorithms
| Algorithm | Rubik's Cube 2x2 (5 moves) | Rubik's Cube 2x2 (10 moves) | Rubik's Cube 3x3 (7 moves) |
|------------|-----------------------------|------------------------------|-----------------------------|
| Greedy Best-First | 0.2 s / 187 states* | 0.9 s / 378 states* | 2.5 s / 842 states* |
| A* (Manhattan) | 0.3 s / 145 states | 5.7 s / 2,453 states | 74.5 s / 35,768 states |
| A* (PDB) | 0.2 s / 102 states | 1.8 s / 1,254 states | N/A |
| IDA* (Manhattan) | 0.7 s / 187 states | 12.8 s / 3,021 states | 245.3 s / 51,423 states |
| IDA* (PDB) | 0.3 s / 124 states | 3.2 s / 1,574 states | N/A |

*: Non-optimal solution. N/A: Not applicable (PDB has not been implemented for the 3x3x3 cube)

#### 4.2.3. Comparison Between Pattern Database and DeepCubeA
| Scrambling Depth | PDB (2x2) | DeepCubeA (2x2) | DeepCubeA (3x3) |
|------------------|-----------|-----------------|-----------------|
| 5 moves | 0.2 s / optimal | 0.4 s / optimal | 0.8 s / optimal |
| 10 moves | 1.8 s / optimal | 1.2 s / +0.5 moves | 2.5 s / +1.2 moves |
| 15 moves | 27.5 s / optimal | 2.5 s / +1.3 moves | 5.8 s / +2.5 moves |
| 20 moves | >300 s / N/A | 4.7 s / +2.1 moves | 10.3 s / +3.7 moves |

### 4.3. Visual Results

#### 4.3.1. Comparison of 2x2 Rubik's Cube Solving Results
![Rubik 2x2 Solver Results](rubik_2x2_solver_results.png)

#### 4.3.2. Comparison of 3x3 Rubik's Cube Solving Results
![Rubik 3x3 Solver Results](rubik_solver_results.png)

#### 4.3.3. Visualization of Uninformed Search Algorithms
##### Rubik's Cube 2x2
![Uninformed Search for 2x2 Rubik's Cube](visualizations/2x2_uninformed_search.png)

##### Rubik's Cube 3x3
![Uninformed Search for 3x3 Rubik's Cube](visualizations/3x3_uninformed_search.png)

#### 4.3.4. Visualization of Informed Search Algorithms
##### Rubik's Cube 2x2
![Informed Search for 2x2 Rubik's Cube](visualizations/2x2_informed_search.png)

##### Rubik's Cube 3x3
![Informed Search for 3x3 Rubik's Cube](visualizations/3x3_informed_search.png)

![Software Interface](3x3GIF/A-star_3x3.gif)

### 4.4. Animated Algorithm Simulations

#### 4.4.1. Solving the 2x2x2 Rubik's Cube

##### Uninformed Search Algorithms
![BFS for 2x2](2x2GIF/BFS_2x2.gif)
![DFS for 2x2](2x2GIF/DFS_2x2.gif)
![IDS for 2x2](2x2GIF/IDS_2x2.gif)
![UCS for 2x2](2x2GIF/UCS_2x2.gif)

##### Informed Search Algorithms
![A* for 2x2](2x2GIF/A-star_2x2.gif)
![Greedy Search for 2x2](2x2GIF/Greedy_Search_2x2.gif)
![IDA* for 2x2](2x2GIF/IDA-star_2x2.gif)
![Pattern Database for 2x2](2x2GIF/Pattern_Database_2x2.gif)

##### Local Search Algorithms
![Simple Hill Climbing for 2x2](2x2GIF/Simple_Hill_2x2.gif)
![Steepest Hill Climbing for 2x2](2x2GIF/Steepest_Hill_2x2.gif)
![Stochastic Hill Climbing for 2x2](2x2GIF/Stochastic_Hill_2x2.gif)
![Simulated Annealing for 2x2](2x2GIF/Simulated_Annealing_2x2.gif)
![Genetic Algorithm for 2x2](2x2GIF/Genetic_2x2.gif)
![Local Beam Search for 2x2](2x2GIF/Local_Beam_2x2.gif)

##### Advanced Algorithms
![DeepCube for 2x2](2x2GIF/Deepcube_2x2.gif)
![And-Or Graph Search for 2x2](2x2GIF/And-Or_2x2.gif)
![Belief State Search for 2x2](2x2GIF/Belief_State_2x2.gif)

#### 4.4.2. Solving the 3x3x3 Rubik's Cube

##### Uninformed Search Algorithms
![BFS for 3x3](3x3GIF/BFS_3x3.gif)
![DFS for 3x3](3x3GIF/DFS_3x3.gif)
![IDS for 3x3](3x3GIF/IDS_3x3.gif)
![UCS for 3x3](3x3GIF/UCS_3x3.gif)

##### Informed Search Algorithms
![A* for 3x3](3x3GIF/A-star_3x3.gif)
![Greedy Search for 3x3](3x3GIF/Greedy_Search_3x3.gif)
![IDA* for 3x3](3x3GIF/IDA-star_3x3.gif)

##### Local Search Algorithms
![Simple Hill Climbing for 3x3](3x3GIF/Simple_Hill_3x3.gif)
![Steepest Hill Climbing for 3x3](3x3GIF/Steepest_Hill_3x3.gif)
![Stochastic Hill Climbing for 3x3](3x3GIF/Stochastic_Hill_3x3.gif)
![Simulated Annealing for 3x3](3x3GIF/Simulated_Annealing_3x3.gif)
![Genetic Algorithm for 3x3](3x3GIF/Genetic_3x3.gif)
![Local Beam Search for 3x3](3x3GIF/Local_Beam_Search_3x3.gif)

##### Advanced Algorithms
![DeepCube for 3x3](3x3GIF/DeepCube_3x3.gif)
![And-Or Graph Search for 3x3](3x3GIF/And-Or_3x3.gif)
![Belief State Search for 3x3](3x3GIF/Belief_state_3x3.gif)

##### CSP Algorithm
![CSP](3x3GIF/CSP.gif)

## 5. Conclusion

### 5.1. Evaluation of the Achieved Results

The "3D Rubik Simulator & Solver" project successfully accomplished the following:

1. **Built an interactive 3D simulation** for 2x2 and 3x3 Rubik's Cubes with an intuitive interface.
2. **Implemented and compared a variety of AI algorithms**, ranging from basic algorithms such as BFS and DFS to advanced approaches such as A*, IDA*, and DeepCubeA.
3. **Conducted detailed performance analysis**, including computation time, memory usage, and solution length.
4. **Illustrated theoretical concepts through practical examples** by visualizing the state space and search process.

**Key findings**:
- Uninformed search algorithms are inefficient for the 3x3 Rubik's Cube because of its enormous state space.
- Pattern Databases provide accurate heuristics but require significant preprocessing time and memory.
- DeepCubeA provides a strong balance between computation time and solution quality, especially for deeply scrambled states.

### 5.2. Future Development

1. **Improve the Pattern Database**:
   - Extend the PDB to the 3x3x3 cube using compression and partitioning techniques
   - Implement Additive Pattern Databases to improve heuristic quality

2. **Enhance the deep-learning model**:
   - Train DeepCubeA at greater scrambling depths (>20 moves)
   - Experiment with alternative network architectures such as CNNs and Transformers

3. **Optimize performance**:
   - Implement parallel processing for traditional search algorithms
   - Accelerate 3D graphics and rendering

4. **Expand the project scope**:
   - Add support for larger Rubik's Cubes, such as 4x4x4 and 5x5x5
   - Implement other Rubik's Cube variants, such as the Mirror Cube and Pyraminx

## 🔗 Links and Resources

- **Detailed report:** [https://1drv.ms/w/c/02781ffec0781aa3/ERCjZMYslV5EguWVHXl1W1sBEMeLfS_eqCgx8t4cwTJ_ow]

## 📋 Authors

**Students:**
- Phan Quốc Viễn - 23110362
- Nguyễn Nhật Huy - 23110226

**Supervisor:** [Dr. Phan Thị Huyền Trang]
