import heapq
import time
from collections import deque
from queue import PriorityQueue
from RubikState.rubik_chen import RubikState, SOLVED_STATE as SOLVED_STATE_3X3, MOVES as MOVES_3X3, heuristic as heuristic_3x3
from RubikState.rubik_2x2 import Rubik2x2State, SOLVED_STATE as SOLVED_STATE_2X2, MOVES as MOVES_2X2, heuristic as heuristic_2x2

def a_star_3x3(start_state, goal_state=None, moves_dict=None):
    """
    Thuật toán A* để giải Rubik's cube 3x3
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_3X3)
        moves_dict: Từ điển nước đi (mặc định là MOVES_3X3)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_3X3
    
    if moves_dict is None:
        moves_dict = MOVES_3X3
    
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

        if time.time() - start_time > 30:  # Giới hạn thời gian 30 giây
            return None, nodes_visited, time.time() - start_time

    return None, nodes_visited, time.time() - start_time

def a_star_2x2(start_state, goal_state=None, moves_dict=None):
    """
    Thuật toán A* để giải Rubik's cube 2x2
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_2X2)
        moves_dict: Từ điển nước đi (mặc định là MOVES_2X2)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_2X2
    
    if moves_dict is None:
        moves_dict = MOVES_2X2
    
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

        if time.time() - start_time > 30:  # Giới hạn thời gian 30 giây
            return None, nodes_visited, time.time() - start_time

    return None, nodes_visited, time.time() - start_time

def bfs_3x3(start_state, goal_state=None, moves_dict=None):
    """
    Thuật toán BFS để giải Rubik's cube 3x3
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_3X3)
        moves_dict: Từ điển nước đi (mặc định là MOVES_3X3)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_3X3
    
    if moves_dict is None:
        moves_dict = MOVES_3X3
    
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
        
        if time.time() - start_time > 30:  # Giới hạn thời gian 30 giây
            return None, nodes_visited, time.time() - start_time
    
    return None, nodes_visited, time.time() - start_time

def bfs_2x2(start_state, goal_state=None, moves_dict=None):
    """
    Thuật toán BFS để giải Rubik's cube 2x2
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE_2X2)
        moves_dict: Từ điển nước đi (mặc định là MOVES_2X2)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_2X2
    
    if moves_dict is None:
        moves_dict = MOVES_2X2
    
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
        
        if time.time() - start_time > 30:  # Giới hạn thời gian 30 giây
            return None, nodes_visited, time.time() - start_time
    
    return None, nodes_visited, time.time() - start_time

def a_star(start_state, goal_state=None, moves_dict=None):
    """
    Tự động gọi thuật toán A* phù hợp dựa vào kiểu của trạng thái đầu vào
    """
    if isinstance(start_state, RubikState):
        return a_star_3x3(start_state, goal_state, moves_dict)
    elif isinstance(start_state, Rubik2x2State):
        return a_star_2x2(start_state, goal_state, moves_dict)
    else:
        raise ValueError("Trạng thái đầu vào không phải là RubikState hoặc Rubik2x2State")

def bfs(start_state, goal_state=None, moves_dict=None):
    """
    Tự động gọi thuật toán BFS phù hợp dựa vào kiểu của trạng thái đầu vào
    """
    if isinstance(start_state, RubikState):
        return bfs_3x3(start_state, goal_state, moves_dict)
    elif isinstance(start_state, Rubik2x2State):
        return bfs_2x2(start_state, goal_state, moves_dict)
    else:
        raise ValueError("Trạng thái đầu vào không phải là RubikState hoặc Rubik2x2State")

# Phần mã thử nghiệm này sẽ chỉ chạy khi tệp này được thực thi trực tiếp
if __name__ == "__main__":
    # Tạo trạng thái ban đầu cho Rubik 3x3 (xáo trộn nhẹ)
    start_state_3x3 = SOLVED_STATE_3X3.copy()
    start_state_3x3 = start_state_3x3.apply_move("R", MOVES_3X3)
    start_state_3x3 = start_state_3x3.apply_move("U", MOVES_3X3)
    
    # Tạo trạng thái ban đầu cho Rubik 2x2 (xáo trộn nhẹ)
    start_state_2x2 = SOLVED_STATE_2X2.copy()
    start_state_2x2 = start_state_2x2.apply_move("R", MOVES_2X2)
    start_state_2x2 = start_state_2x2.apply_move("U", MOVES_2X2)
    start_state_2x2 = start_state_2x2.apply_move("U", MOVES_2X2)
    
    print("Giải Rubik 3x3 bằng A*:")
    path, nodes_visited, time_taken = a_star(start_state_3x3)
    if path:
        print("Đường đi:", path)
        print(f"Thời gian: {time_taken:.2f} giây")
        print("Số node đã duyệt:", nodes_visited)
    else:
        print("Không tìm thấy lời giải")
        print(f"Thời gian: {time_taken:.2f} giây")
        print("Số node đã duyệt:", nodes_visited)

    print("\nGiải Rubik 2x2 bằng A*:")
    path, nodes_visited, time_taken = a_star(start_state_2x2)
    if path:
        print("Đường đi:", path)
        print(f"Thời gian: {time_taken:.2f} giây")
        print("Số node đã duyệt:", nodes_visited)
    else:
        print("Không tìm thấy lời giải")
        print(f"Thời gian: {time_taken:.2f} giây")
        print("Số node đã duyệt:", nodes_visited)