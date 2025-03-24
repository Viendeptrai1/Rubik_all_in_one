import heapq
import time
from collections import deque
from queue import PriorityQueue
from rubik_chen import *
from rubik_2x2 import *

def a_star(start_state, goal_state=None, moves_dict=None):
    """
    Thuật toán A* để giải Rubik's cube
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE)
        moves_dict: Từ điển nước đi (mặc định là MOVES)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE
    
    if moves_dict is None:
        moves_dict = MOVES
    
    # Lấy danh sách tên nước đi từ moves_dict
    move_names = list(moves_dict.keys())
    
    # Đếm số node đã duyệt
    nodes_visited = 0
    
    counter = 0  # Counter to break ties in heap
    queue = [(heuristic(start_state), 0, counter, start_state, [])]
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
                h_score = heuristic(new_state)
                f_score = new_g_score + h_score
                heapq.heappush(queue, (f_score, new_g_score, counter, new_state, path + [move]))
                counter += 1

        if time.time() - start_time > 30:  # Giới hạn thời gian 30 giây
            return None, nodes_visited, time.time() - start_time

    return None, nodes_visited, time.time() - start_time

def bfs(start_state, goal_state=None, moves_dict=None):
    """
    Thuật toán BFS để giải Rubik's cube
    
    Args:
        start_state: Trạng thái bắt đầu
        goal_state: Trạng thái đích (mặc định là SOLVED_STATE)
        moves_dict: Từ điển nước đi (mặc định là MOVES)
    
    Returns:
        tuple: (đường đi, số node đã duyệt, thời gian)
    """
    if goal_state is None:
        goal_state = SOLVED_STATE
    
    if moves_dict is None:
        moves_dict = MOVES
    
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

# Phần mã thử nghiệm này sẽ chỉ chạy khi tệp này được thực thi trực tiếp
if __name__ == "__main__":
    # Tạo trạng thái ban đầu (xáo trộn nhẹ)
    start_state = SOLVED_STATE.copy()
    start_state = start_state.apply_move("R", MOVES)
    start_state = start_state.apply_move("U", MOVES)
    rubik2x2_start_state = Rubik2x2State(cp=start_state.cp[:8], co=start_state.co[:8])
    
    rubik2x2 = Rubik2x2State(
    
        cp=start_state.cp[:8], 
        co=start_state.co[:8]
    )
    rubik2x2 = rubik2x2.apply_move("R", MOVES)
    rubik2x2 = rubik2x2.apply_move("U", MOVES)
    rubik2x2 = rubik2x2.apply_move("U", MOVES)
    
    
    print("Giải bằng A*:")
    path, nodes_visited, time_taken = a_star(start_state)
    if path:
        print("Đường đi:", path)
        print(f"Thời gian: {time_taken:.2f} giây")
        print("Số node đã duyệt:", nodes_visited)
    else:
        print("Không tìm thấy lời giải")
        print(f"Thời gian: {time_taken:.2f} giây")
        print("Số node đã duyệt:", nodes_visited)

    # Giải rubik 2x2 bằng A*
    print("Giải Rubik 2x2 bằng A*:")
    path, nodes_visited, time_taken = a_star(rubik2x2, rubik2x2_start_state, MOVES)
    if path:
        print("Đường đi:", path)
        print(f"Thời gian: {time_taken:.2f} giây")
        print("Số node đã duyệt:", nodes_visited)
    else:
        print("Không tìm thấy lời giải")
        print(f"Thời gian: {time_taken:.2f} giây")
        print("Số node đã duyệt:", nodes_visited)