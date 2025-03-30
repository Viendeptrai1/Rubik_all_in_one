import heapq
import time
from collections import deque
from RubikState.rubik_chen import RubikState, SOLVED_STATE_3x3, MOVES_3x3, heuristic_3x3
from RubikState.rubik_2x2 import Rubik2x2State, SOLVED_STATE_2x2, MOVES_2x2, heuristic_2x2

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


# test_rubik_solver.py


def test_solver(is_2x2=False, algorithm="bfs", scramble_moves=None):
    """Test thuật toán giải Rubik
    
    Args:
        is_2x2: Nếu True, test Rubik 2x2, ngược lại test Rubik 3x3
        algorithm: Thuật toán để test ('bfs' hoặc 'a_star')
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
    
    if algorithm.lower() == "bfs":
        path, nodes_visited, time_taken = bfs(current_state)
    else:  # a_star
        path, nodes_visited, time_taken = a_star(current_state)
    
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
    # Test cho Rubik 2x2 với thuật toán BFS
    test_solver(is_2x2=True, algorithm="bfs")
    
    # Test cho Rubik 2x2 với thuật toán A*
    test_solver(is_2x2=True, algorithm="a_star")
    
    # Test cho Rubik 3x3 với thuật toán BFS (với chuỗi nước đi đơn giản)
    test_solver(is_2x2=False, algorithm="bfs")
    
    # Test cho Rubik 3x3 với thuật toán A* (với chuỗi nước đi đơn giản)
    test_solver(is_2x2=False, algorithm="a_star")
    
    # Test với các nước đi phức tạp hơn (tùy chỉnh)
    complex_moves = ["R", "U", "R'", "U'", "R", "U", "R'", "U'", "F'", "L'", "F", "L"]
    print("\n===== TEST VỚI CÁC NƯỚC ĐI PHỨC TẠP HƠN =====")
    test_solver(is_2x2=True, algorithm="bfs", scramble_moves=complex_moves)

if __name__ == "__main__":
    main()