import heapq
import time
from collections import deque
from RubikState.rubik_chen import RubikState, SOLVED_STATE_3x3, MOVES_3x3, heuristic_3x3
from RubikState.rubik_2x2 import Rubik2x2State, SOLVED_STATE_2x2, MOVES_2x2, heuristic_2x2

def a_star_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Thuật toán A* để giải Rubik's cube 3x3
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_3X3)
        moves_dict: Từ điển nước đi (mặc định là MOVES_3X3)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_3x3
    
    if moves_dict is None:
        moves_dict = MOVES_3x3
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    counter = 0  # Counter to break ties in heap
    queue = [(heuristic_3x3(start_state), 0, counter, start_state, [])]
    visited = {start_state: 0}
    counter += 1

    start_time = time.time()
    while queue:
        _, g_score, _, state, path = heapq.heappop(queue)
        
        if state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time

        for move in move_names:
            nodes_visited += 1
            new_state = state.apply_move(move, moves_dict)
            new_g_score = g_score + 1
            
            if new_state not in visited or new_g_score < visited[new_state]:
                visited[new_state] = new_g_score
                h_score = heuristic_3x3(new_state)
                f_score = new_g_score + h_score
                heapq.heappush(queue, (f_score, new_g_score, counter, new_state, path + [move]))
                counter += 1

        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time

    return None, nodes_visited, time.time() - start_time

def a_star_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Thuật toán A* để giải Rubik's cube 2x2
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_2X2)
        moves_dict: Từ điển nước đi (mặc định là MOVES_2X2)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_2x2
    
    if moves_dict is None:
        moves_dict = MOVES_2x2
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    counter = 0  # Counter to break ties in heap
    queue = [(heuristic_2x2(start_state), 0, counter, start_state, [])]
    visited = {start_state: 0}
    counter += 1

    start_time = time.time()
    while queue:
        _, g_score, _, state, path = heapq.heappop(queue)
        
        if state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time

        for move in move_names:
            nodes_visited += 1
            new_state = state.apply_move(move, moves_dict)
            new_g_score = g_score + 1
            
            if new_state not in visited or new_g_score < visited[new_state]:
                visited[new_state] = new_g_score
                h_score = heuristic_2x2(new_state)
                f_score = new_g_score + h_score
                heapq.heappush(queue, (f_score, new_g_score, counter, new_state, path + [move]))
                counter += 1

        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time

    return None, nodes_visited, time.time() - start_time

def bfs_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Thuật toán BFS để giải Rubik's cube 3x3
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_3X3)
        moves_dict: Từ điển nước đi (mặc định là MOVES_3X3)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_3x3
    
    if moves_dict is None:
        moves_dict = MOVES_3x3
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    queue = deque([(start_state, [])])  # (state, path)
    visited = {start_state}
    
    start_time = time.time()
    while queue:
        state, path = queue.popleft()
        
        if state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        for move in move_names:
            nodes_visited += 1
            new_state = state.apply_move(move, moves_dict)
            
            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, path + [move]))
        
        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time
    
    return None, nodes_visited, time.time() - start_time

def bfs_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Thuật toán BFS để giải Rubik's cube 2x2
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_2X2)
        moves_dict: Từ điển nước đi (mặc định là MOVES_2X2)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_2x2
    
    if moves_dict is None:
        moves_dict = MOVES_2x2
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    queue = deque([(start_state, [])])  # (state, path)
    visited = {start_state}
    
    start_time = time.time()
    while queue:
        state, path = queue.popleft()
        
        if state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        for move in move_names:
            nodes_visited += 1
            new_state = state.apply_move(move, moves_dict)
            
            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, path + [move]))
        
        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time
    
    return None, nodes_visited, time.time() - start_time

def a_star(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """Hàm thống nhất gọi thuật toán A* dựa trên loại khối Rubik"""
    from RubikState.rubik_2x2 import Rubik2x2State
    from RubikState.rubik_chen import RubikState
    
    # Kiểm tra loại trạng thái và chuyển hướng đến hàm thích hợp
    if isinstance(start_state, Rubik2x2State):
        # Try to use PDB version if available
        try:
            from pdb_rubik_2x2 import PatternDatabase, a_star_pdb_2x2
            pdb = PatternDatabase("rubik_2x2_pdb.pkl")
            if pdb.load():
                print("Using Pattern Database heuristic for 2x2...")
                return a_star_pdb_2x2(start_state, goal_state, moves_dict, time_limit, pdb)
        except (ImportError, FileNotFoundError):
            print("Pattern Database not available, using regular A* for 2x2...")
        
        return a_star_2x2(start_state, goal_state, moves_dict, time_limit)
    elif isinstance(start_state, RubikState):
        return a_star_3x3(start_state, goal_state, moves_dict, time_limit)
    else:
        raise ValueError("Unsupported Rubik state type")

def bfs(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Tự động gọi thuật toán BFS phù hợp dựa vào kiểu của trạng thái đầu vào
    """
    if isinstance(start_state, RubikState):
        return bfs_3x3(start_state, goal_state, moves_dict, time_limit)
    elif isinstance(start_state, Rubik2x2State):
        return bfs_2x2(start_state, goal_state, moves_dict, time_limit)
    else:
        raise ValueError("Trạng thái đầu vào không phải là RubikState hoặc Rubik2x2State")

def dfs_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30, max_depth=15):
    """
    Thuật toán DFS để giải Rubik's cube 3x3
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_3X3)
        moves_dict: Từ điển nước đi (mặc định là MOVES_3X3)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
        max_depth: Độ sâu tối đa của DFS (mặc định là 15)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_3x3
    
    if moves_dict is None:
        moves_dict = MOVES_3x3
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    stack = [(start_state, [], 0)]  # (state, path, depth)
    visited = {start_state}
    
    start_time = time.time()
    while stack:
        state, path, depth = stack.pop()
        
        if state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        # Kiểm tra độ sâu
        if depth < max_depth:
            # Thêm các nước đi theo thứ tự ngược lại để ưu tiên các nước đầu
            for move in reversed(move_names):
                nodes_visited += 1
                new_state = state.apply_move(move, moves_dict)
                
                if new_state not in visited:
                    visited.add(new_state)
                    stack.append((new_state, path + [move], depth + 1))
        
        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time
    
    return None, nodes_visited, time.time() - start_time

def dfs_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, max_depth=10):
    """
    Thuật toán DFS để giải Rubik's cube 2x2
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_2X2)
        moves_dict: Từ điển nước đi (mặc định là MOVES_2X2)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
        max_depth: Độ sâu tối đa của DFS (mặc định là 10)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_2x2
    
    if moves_dict is None:
        moves_dict = MOVES_2x2
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    stack = [(start_state, [], 0)]  # (state, path, depth)
    visited = {start_state}
    
    start_time = time.time()
    while stack:
        state, path, depth = stack.pop()
        
        if state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        # Kiểm tra độ sâu
        if depth < max_depth:
            # Thêm các nước đi theo thứ tự ngược lại để ưu tiên các nước đầu
            for move in reversed(move_names):
                nodes_visited += 1
                new_state = state.apply_move(move, moves_dict)
                
                if new_state not in visited:
                    visited.add(new_state)
                    stack.append((new_state, path + [move], depth + 1))
        
        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time
    
    return None, nodes_visited, time.time() - start_time

def dfs(start_state, goal_state=None, moves_dict=None, time_limit=30, max_depth=None):
    """
    Tự động gọi thuật toán DFS phù hợp dựa vào kiểu của trạng thái đầu vào
    """
    if isinstance(start_state, RubikState):
        if max_depth is None:
            max_depth = 15
        return dfs_3x3(start_state, goal_state, moves_dict, time_limit=time_limit, max_depth=max_depth)
    elif isinstance(start_state, Rubik2x2State):
        if max_depth is None:
            max_depth = 10
        return dfs_2x2(start_state, goal_state, moves_dict, time_limit=time_limit, max_depth=max_depth)
    else:
        raise ValueError("Trạng thái đầu vào không phải là RubikState hoặc Rubik2x2State")

def ucs_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Thuật toán UCS (Uniform Cost Search) để giải Rubik's cube 3x3
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_3X3)
        moves_dict: Từ điển nước đi (mặc định là MOVES_3X3)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_3x3
    
    if moves_dict is None:
        moves_dict = MOVES_3x3
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    # Priority queue với cost là độ dài đường đi
    counter = 0  # Dùng để break ties
    queue = [(0, counter, start_state, [])]  # (cost, counter, state, path)
    visited = {start_state: 0}
    
    start_time = time.time()
    while queue:
        cost, _, state, path = heapq.heappop(queue)
        
        if state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        for move in move_names:
            nodes_visited += 1
            new_state = state.apply_move(move, moves_dict)
            new_cost = cost + 1  # Mỗi bước có chi phí = 1
            
            if new_state not in visited or new_cost < visited[new_state]:
                visited[new_state] = new_cost
                counter += 1
                heapq.heappush(queue, (new_cost, counter, new_state, path + [move]))
        
        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time
    
    return None, nodes_visited, time.time() - start_time

def ucs_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Thuật toán UCS (Uniform Cost Search) để giải Rubik's cube 2x2
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_2X2)
        moves_dict: Từ điển nước đi (mặc định là MOVES_2X2)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_2x2
    
    if moves_dict is None:
        moves_dict = MOVES_2x2
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    # Priority queue với cost là độ dài đường đi
    counter = 0  # Dùng để break ties
    queue = [(0, counter, start_state, [])]  # (cost, counter, state, path)
    visited = {start_state: 0}
    
    start_time = time.time()
    while queue:
        cost, _, state, path = heapq.heappop(queue)
        
        if state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        for move in move_names:
            nodes_visited += 1
            new_state = state.apply_move(move, moves_dict)
            new_cost = cost + 1  # Mỗi bước có chi phí = 1
            
            if new_state not in visited or new_cost < visited[new_state]:
                visited[new_state] = new_cost
                counter += 1
                heapq.heappush(queue, (new_cost, counter, new_state, path + [move]))
        
        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time
    
    return None, nodes_visited, time.time() - start_time

def ucs(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Tự động gọi thuật toán UCS phù hợp dựa vào kiểu của trạng thái đầu vào
    """
    if isinstance(start_state, RubikState):
        return ucs_3x3(start_state, goal_state, moves_dict, time_limit)
    elif isinstance(start_state, Rubik2x2State):
        return ucs_2x2(start_state, goal_state, moves_dict, time_limit)
    else:
        raise ValueError("Trạng thái đầu vào không phải là RubikState hoặc Rubik2x2State")

def ids_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30, max_depth=15):
    """
    Thuật toán IDS (Iterative Deepening Search) để giải Rubik's cube 3x3
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_3X3)
        moves_dict: Từ điển nước đi (mặc định là MOVES_3X3)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
        max_depth: Độ sâu tối đa của IDS (mặc định là 15)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_3x3
    
    if moves_dict is None:
        moves_dict = MOVES_3x3
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    # Hàm dfs giới hạn độ sâu (dls)
    def dls(state, depth, path):
        nonlocal nodes_visited
        
        if state == goal_state:
            return path
        
        if depth == 0:
            return None
        
        for move in move_names:
            nodes_visited += 1
            new_state = state.apply_move(move, moves_dict)
            result = dls(new_state, depth - 1, path + [move])
            
            if result is not None:
                return result
        
        return None
    
    start_time = time.time()
    
    # Tăng dần độ sâu từ 1 đến max_depth
    for depth in range(1, max_depth + 1):
        result = dls(start_state, depth, [])
        
        if result is not None:
            end_time = time.time()
            return result, nodes_visited, end_time - start_time
        
        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time
    
    return None, nodes_visited, time.time() - start_time

def ids_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, max_depth=10):
    """
    Thuật toán IDS (Iterative Deepening Search) để giải Rubik's cube 2x2
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_2X2)
        moves_dict: Từ điển nước đi (mặc định là MOVES_2X2)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
        max_depth: Độ sâu tối đa của IDS (mặc định là 10)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_2x2
    
    if moves_dict is None:
        moves_dict = MOVES_2x2
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    # Hàm dfs giới hạn độ sâu (dls)
    def dls(state, depth, path):
        nonlocal nodes_visited
        
        if state == goal_state:
            return path
        
        if depth == 0:
            return None
        
        for move in move_names:
            nodes_visited += 1
            new_state = state.apply_move(move, moves_dict)
            result = dls(new_state, depth - 1, path + [move])
            
            if result is not None:
                return result
        
        return None
    
    start_time = time.time()
    
    # Tăng dần độ sâu từ 1 đến max_depth
    for depth in range(1, max_depth + 1):
        result = dls(start_state, depth, [])
        
        if result is not None:
            end_time = time.time()
            return result, nodes_visited, end_time - start_time
        
        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time
    
    return None, nodes_visited, time.time() - start_time

def ids(start_state, goal_state=None, moves_dict=None, time_limit=30, max_depth=None):
    """
    Tự động gọi thuật toán IDS phù hợp dựa vào kiểu của trạng thái đầu vào
    """
    if isinstance(start_state, RubikState):
        if max_depth is None:
            max_depth = 15
        return ids_3x3(start_state, goal_state, moves_dict, time_limit=time_limit, max_depth=max_depth)
    elif isinstance(start_state, Rubik2x2State):
        if max_depth is None:
            max_depth = 10
        return ids_2x2(start_state, goal_state, moves_dict, time_limit=time_limit, max_depth=max_depth)
    else:
        raise ValueError("Trạng thái đầu vào không phải là RubikState hoặc Rubik2x2State")

def greedy_best_first_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Thuật toán Greedy Best-First Search để giải Rubik's cube 3x3
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_3X3)
        moves_dict: Từ điển nước đi (mặc định là MOVES_3X3)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_3x3
    
    if moves_dict is None:
        moves_dict = MOVES_3x3
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    # Priority queue chỉ dựa trên heuristic
    counter = 0  # Dùng để break ties
    queue = [(heuristic_3x3(start_state), counter, start_state, [])]
    visited = {start_state}
    counter += 1
    
    start_time = time.time()
    while queue:
        _, _, state, path = heapq.heappop(queue)
        
        if state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        for move in move_names:
            nodes_visited += 1
            new_state = state.apply_move(move, moves_dict)
            
            if new_state not in visited:
                visited.add(new_state)
                h_score = heuristic_3x3(new_state)
                counter += 1
                heapq.heappush(queue, (h_score, counter, new_state, path + [move]))
        
        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time
    
    return None, nodes_visited, time.time() - start_time

def greedy_best_first_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Thuật toán Greedy Best-First Search để giải Rubik's cube 2x2
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_2X2)
        moves_dict: Từ điển nước đi (mặc định là MOVES_2X2)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_2x2
    
    if moves_dict is None:
        moves_dict = MOVES_2x2
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    # Priority queue chỉ dựa trên heuristic
    counter = 0  # Dùng để break ties
    queue = [(heuristic_2x2(start_state), counter, start_state, [])]
    visited = {start_state}
    counter += 1
    
    start_time = time.time()
    while queue:
        _, _, state, path = heapq.heappop(queue)
        
        if state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        for move in move_names:
            nodes_visited += 1
            new_state = state.apply_move(move, moves_dict)
            
            if new_state not in visited:
                visited.add(new_state)
                h_score = heuristic_2x2(new_state)
                counter += 1
                heapq.heappush(queue, (h_score, counter, new_state, path + [move]))
        
        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time
    
    return None, nodes_visited, time.time() - start_time

def greedy_best_first(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Tự động gọi thuật toán greedy best-first phù hợp dựa vào kiểu của trạng thái đầu vào
    """
    if isinstance(start_state, RubikState):
        return greedy_best_first_3x3(start_state, goal_state, moves_dict, time_limit)
    elif isinstance(start_state, Rubik2x2State):
        return greedy_best_first_2x2(start_state, goal_state, moves_dict, time_limit)
    else:
        raise ValueError("Trạng thái đầu vào không phải là RubikState hoặc Rubik2x2State")

def ida_star_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Thuật toán IDA* (Iterative Deepening A*) để giải Rubik's cube 3x3
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_3X3)
        moves_dict: Từ điển nước đi (mặc định là MOVES_3X3)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_3x3
    
    if moves_dict is None:
        moves_dict = MOVES_3x3
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    # Hàm dfs có giới hạn (f-limit)
    def search(state, g, path, f_limit):
        nonlocal nodes_visited
        
        f = g + heuristic_3x3(state)
        
        if f > f_limit:
            return f, None
        
        if state == goal_state:
            return -1, path
        
        min_cost = float('inf')
        
        for move in move_names:
            nodes_visited += 1
            new_state = state.apply_move(move, moves_dict)
            new_cost, new_path = search(new_state, g + 1, path + [move], f_limit)
            
            if new_cost == -1:  # Đã tìm thấy đường đi
                return -1, new_path
            
            if new_cost < min_cost:
                min_cost = new_cost
        
        return min_cost, None
    
    start_time = time.time()
    
    # IDA* bắt đầu với f_limit = h(start)
    f_limit = heuristic_3x3(start_state)
    
    while True:
        cost, path = search(start_state, 0, [], f_limit)
        
        if cost == -1:  # Đã tìm thấy đường đi
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        if cost == float('inf'):  # Không có đường đi
            return None, nodes_visited, time.time() - start_time
        
        # Tăng f_limit cho vòng lặp tiếp theo
        f_limit = cost
        
        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time

def ida_star_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Thuật toán IDA* (Iterative Deepening A*) để giải Rubik's cube 2x2
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_2X2)
        moves_dict: Từ điển nước đi (mặc định là MOVES_2X2)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_2x2
    
    if moves_dict is None:
        moves_dict = MOVES_2x2
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    # Hàm dfs có giới hạn (f-limit)
    def search(state, g, path, f_limit):
        nonlocal nodes_visited
        
        f = g + heuristic_2x2(state)
        
        if f > f_limit:
            return f, None
        
        if state == goal_state:
            return -1, path
        
        min_cost = float('inf')
        
        for move in move_names:
            nodes_visited += 1
            new_state = state.apply_move(move, moves_dict)
            new_cost, new_path = search(new_state, g + 1, path + [move], f_limit)
            
            if new_cost == -1:  # Đã tìm thấy đường đi
                return -1, new_path
            
            if new_cost < min_cost:
                min_cost = new_cost
        
        return min_cost, None
    
    start_time = time.time()
    
    # IDA* bắt đầu với f_limit = h(start)
    f_limit = heuristic_2x2(start_state)
    
    while True:
        cost, path = search(start_state, 0, [], f_limit)
        
        if cost == -1:  # Đã tìm thấy đường đi
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        if cost == float('inf'):  # Không có đường đi
            return None, nodes_visited, time.time() - start_time
        
        # Tăng f_limit cho vòng lặp tiếp theo
        f_limit = cost
        
        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time

def hill_climbing_max_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30, max_iterations=1000):
    """
    Thuật toán Hill Climbing Max để giải Rubik's cube 3x3
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_3X3)
        moves_dict: Từ điển nước đi (mặc định là MOVES_3X3)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
        max_iterations: Số lần lặp tối đa (mặc định là 1000)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_3x3
    
    if moves_dict is None:
        moves_dict = MOVES_3x3
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    current_state = start_state
    current_h = heuristic_3x3(current_state)
    path = []
    
    start_time = time.time()
    
    # Lặp cho đến khi đạt mục tiêu hoặc không thể cải thiện thêm
    for _ in range(max_iterations):
        if current_state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        # Tìm neighbor tối ưu nhất
        best_neighbor = None
        best_move = None
        best_h = current_h
        
        for move in move_names:
            nodes_visited += 1
            neighbor = current_state.apply_move(move, moves_dict)
            neighbor_h = heuristic_3x3(neighbor)
            
            # Tìm neighbor có heuristic nhỏ nhất (tốt nhất)
            if neighbor_h < best_h:
                best_neighbor = neighbor
                best_move = move
                best_h = neighbor_h
        
        # Nếu không thể cải thiện, kết thúc
        if best_neighbor is None:
            break
        
        # Di chuyển đến trạng thái tốt nhất
        current_state = best_neighbor
        current_h = best_h
        path.append(best_move)
        
        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time
    
    # Nếu tìm thấy đường đi đến đích, trả về
    if current_state == goal_state:
        end_time = time.time()
        return path, nodes_visited, end_time - start_time
    
    # Không tìm thấy đường đi
    return None, nodes_visited, time.time() - start_time

def hill_climbing_max_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, max_iterations=1000):
    """
    Thuật toán Hill Climbing Max để giải Rubik's cube 2x2
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_2X2)
        moves_dict: Từ điển nước đi (mặc định là MOVES_2X2)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
        max_iterations: Số lần lặp tối đa (mặc định là 1000)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_2x2
    
    if moves_dict is None:
        moves_dict = MOVES_2x2
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    current_state = start_state
    current_h = heuristic_2x2(current_state)
    path = []
    
    start_time = time.time()
    
    # Lặp cho đến khi đạt mục tiêu hoặc không thể cải thiện thêm
    for _ in range(max_iterations):
        if current_state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        # Tìm neighbor tối ưu nhất
        best_neighbor = None
        best_move = None
        best_h = current_h
        
        for move in move_names:
            nodes_visited += 1
            neighbor = current_state.apply_move(move, moves_dict)
            neighbor_h = heuristic_2x2(neighbor)
            
            # Tìm neighbor có heuristic nhỏ nhất (tốt nhất)
            if neighbor_h < best_h:
                best_neighbor = neighbor
                best_move = move
                best_h = neighbor_h
        
        # Nếu không thể cải thiện, kết thúc
        if best_neighbor is None:
            break
        
        # Di chuyển đến trạng thái tốt nhất
        current_state = best_neighbor
        current_h = best_h
        path.append(best_move)
        
        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time
    
    # Nếu tìm thấy đường đi đến đích, trả về
    if current_state == goal_state:
        end_time = time.time()
        return path, nodes_visited, end_time - start_time
    
    # Không tìm thấy đường đi
    return None, nodes_visited, time.time() - start_time

def hill_climbing_random_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30, max_iterations=1000):
    """
    Thuật toán Hill Climbing Random để giải Rubik's cube 3x3
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_3X3)
        moves_dict: Từ điển nước đi (mặc định là MOVES_3X3)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
        max_iterations: Số lần lặp tối đa (mặc định là 1000)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_3x3
    
    if moves_dict is None:
        moves_dict = MOVES_3x3
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    import random
    
    current_state = start_state
    current_h = heuristic_3x3(current_state)
    path = []
    
    start_time = time.time()
    
    # Lặp cho đến khi đạt mục tiêu hoặc không thể cải thiện thêm
    for _ in range(max_iterations):
        if current_state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        # Tìm tất cả các neighbor có heuristic tốt hơn
        better_neighbors = []
        
        for move in move_names:
            nodes_visited += 1
            neighbor = current_state.apply_move(move, moves_dict)
            neighbor_h = heuristic_3x3(neighbor)
            
            # Tìm neighbor có heuristic tốt hơn
            if neighbor_h < current_h:
                better_neighbors.append((neighbor, move, neighbor_h))
        
        # Nếu không thể cải thiện, kết thúc
        if not better_neighbors:
            break
        
        # Chọn ngẫu nhiên một neighbor tốt hơn
        chosen = random.choice(better_neighbors)
        current_state, best_move, current_h = chosen
        path.append(best_move)
        
        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time
    
    # Nếu tìm thấy đường đi đến đích, trả về
    if current_state == goal_state:
        end_time = time.time()
        return path, nodes_visited, end_time - start_time
    
    # Không tìm thấy đường đi
    return None, nodes_visited, time.time() - start_time

def hill_climbing_random_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, max_iterations=1000):
    """
    Thuật toán Hill Climbing Random để giải Rubik's cube 2x2
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_2X2)
        moves_dict: Từ điển nước đi (mặc định là MOVES_2X2)
        time_limit: Giới hạn thời gian (mặc định là 30 giây)
        max_iterations: Số lần lặp tối đa (mặc định là 1000)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_2x2
    
    if moves_dict is None:
        moves_dict = MOVES_2x2
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    import random
    
    current_state = start_state
    current_h = heuristic_2x2(current_state)
    path = []
    
    start_time = time.time()
    
    # Lặp cho đến khi đạt mục tiêu hoặc không thể cải thiện thêm
    for _ in range(max_iterations):
        if current_state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        # Tìm tất cả các neighbor có heuristic tốt hơn
        better_neighbors = []
        
        for move in move_names:
            nodes_visited += 1
            neighbor = current_state.apply_move(move, moves_dict)
            neighbor_h = heuristic_2x2(neighbor)
            
            # Tìm neighbor có heuristic tốt hơn
            if neighbor_h < current_h:
                better_neighbors.append((neighbor, move, neighbor_h))
        
        # Nếu không thể cải thiện, kết thúc
        if not better_neighbors:
            break
        
        # Chọn ngẫu nhiên một neighbor tốt hơn
        chosen = random.choice(better_neighbors)
        current_state, best_move, current_h = chosen
        path.append(best_move)
        
        if time.time() - start_time > time_limit:  # Giới hạn thời gian
            return None, nodes_visited, time.time() - start_time
    
    # Nếu tìm thấy đường đi đến đích, trả về
    if current_state == goal_state:
        end_time = time.time()
        return path, nodes_visited, end_time - start_time
    
    # Không tìm thấy đường đi
    return None, nodes_visited, time.time() - start_time

def greedy_best_first(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Tự động gọi thuật toán greedy best-first phù hợp dựa vào kiểu của trạng thái đầu vào
    """
    if isinstance(start_state, RubikState):
        return greedy_best_first_3x3(start_state, goal_state, moves_dict, time_limit)
    elif isinstance(start_state, Rubik2x2State):
        return greedy_best_first_2x2(start_state, goal_state, moves_dict, time_limit)
    else:
        raise ValueError("Trạng thái đầu vào không phải là RubikState hoặc Rubik2x2State")

def ida_star(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Tự động gọi thuật toán IDA* phù hợp dựa vào kiểu của trạng thái đầu vào
    """
    if isinstance(start_state, RubikState):
        return ida_star_3x3(start_state, goal_state, moves_dict, time_limit)
    elif isinstance(start_state, Rubik2x2State):
        return ida_star_2x2(start_state, goal_state, moves_dict, time_limit)
    else:
        raise ValueError("Trạng thái đầu vào không phải là RubikState hoặc Rubik2x2State")

def hill_climbing_max(start_state, goal_state=None, moves_dict=None, time_limit=30, max_iterations=None):
    """
    Tự động gọi thuật toán Hill Climbing Max phù hợp dựa vào kiểu của trạng thái đầu vào
    """
    if isinstance(start_state, RubikState):
        if max_iterations is None:
            max_iterations = 1000
        return hill_climbing_max_3x3(start_state, goal_state, moves_dict, time_limit=time_limit, max_iterations=max_iterations)
    elif isinstance(start_state, Rubik2x2State):
        if max_iterations is None:
            max_iterations = 1000
        return hill_climbing_max_2x2(start_state, goal_state, moves_dict, time_limit=time_limit, max_iterations=max_iterations)
    else:
        raise ValueError("Trạng thái đầu vào không phải là RubikState hoặc Rubik2x2State")

def hill_climbing_random(start_state, goal_state=None, moves_dict=None, time_limit=30, max_iterations=None):
    """
    Tự động gọi thuật toán Hill Climbing Random phù hợp dựa vào kiểu của trạng thái đầu vào
    """
    if isinstance(start_state, RubikState):
        if max_iterations is None:
            max_iterations = 1000
        return hill_climbing_random_3x3(start_state, goal_state, moves_dict, time_limit=time_limit, max_iterations=max_iterations)
    elif isinstance(start_state, Rubik2x2State):
        if max_iterations is None:
            max_iterations = 1000
        return hill_climbing_random_2x2(start_state, goal_state, moves_dict, time_limit=time_limit, max_iterations=max_iterations)
    else:
        raise ValueError("Trạng thái đầu vào không phải là RubikState hoặc Rubik2x2State")

def test_solver(is_2x2=False, algorithm="bfs", scramble_moves=None):
    """Test thuật toán giải Rubik
    
    Args:
        is_2x2: Nếu True, test Rubik 2x2, ngược lại test Rubik 3x3
        algorithm: Thuật toán để test ('bfs', 'dfs', 'ucs', 'ids', 'a_star', 'ida_star', 'greedy', 'hill_climbing_max', 'hill_climbing_random')
        scramble_moves: List các nước đi để xáo trộn, nếu None sẽ dùng mặc định
    
    Returns:
        True nếu thuật toán giải thành công, False nếu không
    """
    print(f"\n===== TEST THUẬT TOÁN {algorithm.upper()} CHO {'RUBIK 2X2' if is_2x2 else 'RUBIK 3X3'} =====")
    
    # Tạo trạng thái ban đầu (đã giải) và chọn đúng tập nước đi
    if is_2x2:
        solved_state = SOLVED_STATE_2x2
        moves_dict = MOVES_2x2
        state_class = Rubik2x2State
    else:
        solved_state = SOLVED_STATE_3x3
        moves_dict = MOVES_3x3
        state_class = RubikState
    
    # Xác định nước đi xáo trộn nếu không cung cấp
    if scramble_moves is None:
        if is_2x2:
            # Các nước đi đơn giản cho Rubik 2x2
            scramble_moves = ["R", "U", "R'", "U'", "R", "U", "R'"]
        else:
            # Các nước đi đơn giản cho Rubik 3x3
            scramble_moves = ["R", "U", "R'", "U'", "F'", "L", "F"]
    
    # In ra các nước xáo trộn
    print(f"Xáo trộn với các nước đi: {' '.join(scramble_moves)}")
    
    # Tạo trạng thái bị xáo trộn
    scrambled_state = solved_state.copy()
    for move in scramble_moves:
        scrambled_state = scrambled_state.apply_move(move, moves_dict)
    
    print(f"Trạng thái ban đầu:")
    if is_2x2:
        print(f"cp: {scrambled_state.cp}")
        print(f"co: {scrambled_state.co}")
    else:
        print(f"cp: {scrambled_state.cp}")
        print(f"co: {scrambled_state.co}")
        print(f"ep: {scrambled_state.ep}")
        print(f"eo: {scrambled_state.eo}")
    
    # Tạo trạng thái ban đầu cho thuật toán giải 
    if is_2x2:
        # Lấy cp và co từ trạng thái bị xáo trộn
        cp = scrambled_state.cp
        co = scrambled_state.co
        current_state = Rubik2x2State(cp, co)
    else:
        # Lấy cp, co, ep, eo từ trạng thái bị xáo trộn
        cp = scrambled_state.cp
        co = scrambled_state.co
        ep = scrambled_state.ep
        eo = scrambled_state.eo
        current_state = RubikState(cp, co, ep, eo)
    
    # Gọi thuật toán giải
    print(f"Đang giải bằng thuật toán {algorithm}...")
    start_time = time.time()
    
    # Chọn thuật toán phù hợp
    if algorithm.lower() == "bfs":
        path, nodes_visited, time_taken = bfs(current_state)
    elif algorithm.lower() == "dfs":
        path, nodes_visited, time_taken = dfs(current_state)
    elif algorithm.lower() == "ucs":
        path, nodes_visited, time_taken = ucs(current_state)
    elif algorithm.lower() == "ids":
        path, nodes_visited, time_taken = ids(current_state)
    elif algorithm.lower() == "a_star":
        path, nodes_visited, time_taken = a_star(current_state)
    elif algorithm.lower() == "ida_star":
        path, nodes_visited, time_taken = ida_star(current_state)
    elif algorithm.lower() == "greedy":
        path, nodes_visited, time_taken = greedy_best_first(current_state)
    elif algorithm.lower() == "hill_climbing_max":
        path, nodes_visited, time_taken = hill_climbing_max(current_state)
    elif algorithm.lower() == "hill_climbing_random":
        path, nodes_visited, time_taken = hill_climbing_random(current_state)
    else:
        print(f"Thuật toán không hợp lệ: {algorithm}")
        return False
    
    # Kiểm tra kết quả
    if path:
        print(f"Đã tìm được lời giải trong {time_taken:.2f} giây")
        print(f"Số nút đã duyệt: {nodes_visited}")
        print(f"Độ dài lời giải: {len(path)}")
        print(f"Lời giải: {' '.join(path)}")
        
        # Kiểm tra xem lời giải có đúng không
        test_state = current_state.copy()
        for move in path:
            test_state = test_state.apply_move(move, moves_dict)
        
        # So sánh với trạng thái đã giải
        is_solved = (test_state == solved_state)
        print(f"Lời giải có đúng không? {'CÓ' if is_solved else 'KHÔNG'}")
        
        if not is_solved:
            print("Trạng thái sau khi áp dụng lời giải:")
            if is_2x2:
                print(f"cp: {test_state.cp}")
                print(f"co: {test_state.co}")
            else:
                print(f"cp: {test_state.cp}")
                print(f"co: {test_state.co}")
                print(f"ep: {test_state.ep}")
                print(f"eo: {test_state.eo}")
            
            print("Trạng thái đã giải:")
            if is_2x2:
                print(f"cp: {solved_state.cp}")
                print(f"co: {solved_state.co}")
            else:
                print(f"cp: {solved_state.cp}")
                print(f"co: {solved_state.co}")
                print(f"ep: {solved_state.ep}")
                print(f"eo: {solved_state.eo}")
        
        return is_solved
    else:
        print(f"Không tìm thấy lời giải trong thời gian cho phép!")
        return False

def main():
    # Test cho Rubik 2x2 với các thuật toán khác nhau
    algorithms = [
        "bfs", "dfs", "ucs", "ids", "a_star", "ida_star", "greedy", 
        "hill_climbing_max", "hill_climbing_random"
    ]
    
    # Test với một vài thuật toán cơ bản
    test_solver(is_2x2=True, algorithm="bfs")
    test_solver(is_2x2=True, algorithm="dfs")
    test_solver(is_2x2=True, algorithm="a_star")
    
    # Test với Rubik 3x3 (với chuỗi nước đi đơn giản)
    test_solver(is_2x2=False, algorithm="bfs")
    
    # Test với các nước đi phức tạp hơn
    complex_moves = ["R", "U", "R'", "U'", "R", "U", "R'", "U'", "F'", "L'", "F", "L"]
    print("\n===== TEST VỚI CÁC NƯỚC ĐI PHỨC TẠP HƠN =====")
    test_solver(is_2x2=True, algorithm="bfs", scramble_moves=complex_moves)

