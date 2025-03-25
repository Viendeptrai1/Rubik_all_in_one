import heapq
import time
import random
from collections import deque
from rubik_state import RubikState, SOLVED_STATE, apply_move, MOVE_NAMES, heuristic, generate_random_state

class Node:
    """Node trong cây tìm kiếm"""
    def __init__(self, state, parent=None, move=None, g=0, h=0):
        self.state = state  # Trạng thái Rubik
        self.parent = parent  # Node cha
        self.move = move  # Nước đi để đến node này từ node cha
        self.g = g  # Chi phí từ node gốc đến node này
        self.h = h  # Đánh giá heuristic
        self.f = g + h  # Tổng chi phí
    
    def __lt__(self, other):
        # So sánh cho hàng đợi ưu tiên
        if self.f == other.f:
            return self.h < other.h  # Ưu tiên node có heuristic thấp hơn
        return self.f < other.f

def get_solution_path(node):
    """Lấy chuỗi các nước đi từ node gốc đến node hiện tại"""
    path = []
    current = node
    while current.parent:
        path.append(current.move)
        current = current.parent
    path.reverse()
    return path

def get_opposite_move(move):
    """Lấy nước đi ngược lại"""
    if "'" in move:
        return move[0]
    elif "2" in move:
        return move  # Nước đi 2 lần là đối ngẫu của chính nó
    else:
        return move + "'"

def get_move_sequence(moves):
    """Chuyển đổi danh sách nước đi thành chuỗi"""
    return " ".join(moves)

def is_redundant_move_sequence(last_moves, new_move):
    """Kiểm tra xem một nước đi mới có dẫn đến tình trạng dư thừa không"""
    if not last_moves:
        return False
    
    # Không thực hiện nước đi ngược ngay lập tức
    if len(last_moves) >= 1 and new_move == get_opposite_move(last_moves[-1]):
        return True
    
    # Không xoay cùng một mặt nhiều lần liên tiếp
    if len(last_moves) >= 1 and new_move[0] == last_moves[-1][0]:
        return True
    
    # Không thực hiện các chuỗi nước đi vô nghĩa (ví dụ: R L R' L')
    if len(last_moves) >= 3 and new_move == get_opposite_move(last_moves[-3]) and last_moves[-1] == get_opposite_move(last_moves[-2]):
        return True
    
    return False

def a_star_search(initial_state, max_depth=25, time_limit=60, use_advanced_pruning=True):
    """Thuật toán A* để tìm lời giải cho Rubik với các chiến lược cắt tỉa nâng cao"""
    start_time = time.time()
    initial_h = heuristic(initial_state)
    
    # Kiểm tra nếu trạng thái ban đầu đã là trạng thái đích
    if initial_state == SOLVED_STATE:
        return {
            "solution": [],
            "nodes_explored": 0,
            "time": 0,
            "depth": 0,
            "algorithm": "a_star"
        }
    
    # Khởi tạo tập mở và đóng
    open_set = []
    heapq.heappush(open_set, Node(initial_state, None, None, 0, initial_h))
    closed_set = set()  # Lưu hash của các trạng thái đã xét
    
    # Đếm số nodes đã khám phá
    nodes_explored = 0
    max_queue_size = 1
    
    # Cập nhật thông tin status mỗi 1000 nodes
    status_interval = 1000
    
    while open_set and time.time() - start_time < time_limit:
        # Cập nhật max queue size
        max_queue_size = max(max_queue_size, len(open_set))
        
        # Lấy node có f nhỏ nhất
        current = heapq.heappop(open_set)
        
        # Nếu đã đạt đến trạng thái đích
        if current.state == SOLVED_STATE:
            solution = get_solution_path(current)
            return {
                "solution": solution,
                "nodes_explored": nodes_explored,
                "time": time.time() - start_time,
                "depth": current.g,
                "algorithm": "a_star",
                "max_queue_size": max_queue_size
            }
        
        # Thêm vào tập đóng
        state_hash = hash(current.state)
        if state_hash in closed_set:
            continue
        closed_set.add(state_hash)
        
        # Kiểm tra độ sâu
        if current.g >= max_depth:
            continue
        
        # Tạo các node con
        nodes_explored += 1
        
        # In thông tin trạng thái nếu cần
        if nodes_explored % status_interval == 0:
            elapsed_time = time.time() - start_time
            print(f"[A*] Nodes explored: {nodes_explored}, Queue size: {len(open_set)}, Time: {elapsed_time:.2f}s")
        
        # Lấy các nước đi đã thực hiện để đến node hiện tại
        last_moves = []
        current_node = current
        for _ in range(min(3, current.g)):  # Chỉ xem xét 3 nước đi gần nhất
            if current_node.move:
                last_moves.insert(0, current_node.move)
            current_node = current_node.parent
            if not current_node:
                break
        
        # Không thực hiện nước đi ngược với nước đi gần nhất
        last_move = current.move
        opposite_move = get_opposite_move(last_move) if last_move else None
        
        for move in MOVE_NAMES:
            # Tránh thực hiện nước đi đối lập với nước vừa thực hiện
            if move == opposite_move:
                continue
            
            # Các chiến lược cắt tỉa nâng cao
            if use_advanced_pruning and is_redundant_move_sequence(last_moves, move):
                continue
            
            # Áp dụng nước đi để tạo trạng thái mới
            new_state = apply_move(current.state, move)
            
            # Tính chi phí mới
            new_g = current.g + 1
            new_h = heuristic(new_state)
            
            # Tạo node mới và thêm vào tập mở
            heapq.heappush(open_set, Node(new_state, current, move, new_g, new_h))
    
    # Không tìm thấy lời giải trong giới hạn thời gian hoặc độ sâu
    return {
        "solution": None,
        "nodes_explored": nodes_explored,
        "time": time.time() - start_time,
        "depth": None,
        "algorithm": "a_star",
        "max_queue_size": max_queue_size
    }

def ida_star_search(initial_state, max_depth=25, time_limit=60, use_advanced_pruning=True):
    """Thuật toán IDA* để tìm lời giải cho Rubik với các chiến lược cắt tỉa nâng cao"""
    start_time = time.time()
    
    # Kiểm tra nếu trạng thái ban đầu đã là trạng thái đích
    if initial_state == SOLVED_STATE:
        return {
            "solution": [],
            "nodes_explored": 0,
            "time": 0,
            "depth": 0,
            "algorithm": "ida_star"
        }
    
    # Khởi tạo các biến
    initial_h = heuristic(initial_state)
    f_limit = initial_h
    nodes_explored = 0
    status_interval = 1000
    
    # Hàm DFS giới hạn với các chiến lược cắt tỉa nâng cao
    def search(node, g, f_limit, path, visited):
        nonlocal nodes_explored, start_time, status_interval
        
        # Kiểm tra thời gian
        if time.time() - start_time > time_limit:
            return float('inf'), None
        
        # Tính f-value
        f = g + heuristic(node.state)
        
        # In thông tin trạng thái nếu cần
        if nodes_explored % status_interval == 0:
            elapsed_time = time.time() - start_time
            print(f"[IDA*] Nodes explored: {nodes_explored}, Current depth: {g}, f-limit: {f_limit}, Time: {elapsed_time:.2f}s")
        
        # Nếu f vượt quá giới hạn, trả về
        if f > f_limit:
            return f, None
        
        # Nếu đạt đến trạng thái đích
        if node.state == SOLVED_STATE:
            return f, path
        
        # Nếu đã đạt đến độ sâu tối đa
        if g >= max_depth:
            return f, None
        
        # Thêm vào tập đã thăm
        state_hash = hash(node.state)
        if state_hash in visited and visited[state_hash] <= g:
            return float('inf'), None
        visited[state_hash] = g
        
        nodes_explored += 1
        min_cost = float('inf')
        best_path = None
        
        # Lấy các nước đi đã thực hiện
        last_moves = path[-3:] if len(path) >= 3 else path
        
        # Không thực hiện nước đi ngược với nước đi gần nhất
        last_move = path[-1] if path else None
        opposite_move = get_opposite_move(last_move) if last_move else None
        
        # Sắp xếp các nước đi theo heuristic để tăng hiệu suất
        moves_with_heuristic = []
        for move in MOVE_NAMES:
            # Tránh thực hiện nước đi đối lập với nước vừa thực hiện
            if move == opposite_move:
                continue
            
            # Các chiến lược cắt tỉa nâng cao
            if use_advanced_pruning and is_redundant_move_sequence(last_moves, move):
                continue
            
            # Dự đoán heuristic sau khi áp dụng nước đi
            new_state = apply_move(node.state, move)
            move_h = heuristic(new_state)
            moves_with_heuristic.append((move, move_h, new_state))
        
        # Sắp xếp các nước đi theo heuristic tăng dần
        moves_with_heuristic.sort(key=lambda x: x[1])
        
        for move, _, new_state in moves_with_heuristic:
            # Tạo node mới và thực hiện tìm kiếm đệ quy
            new_node = Node(new_state, node, move, g + 1, 0)
            new_path = path + [move]
            
            cost, result = search(new_node, g + 1, f_limit, new_path, visited)
            
            if result is not None:
                return cost, result
            
            if cost < min_cost:
                min_cost = cost
        
        return min_cost, best_path
    
    # Lặp với các giới hạn f tăng dần
    while f_limit <= max_depth * 2 and time.time() - start_time < time_limit:
        # Thực hiện tìm kiếm với giới hạn f hiện tại
        print(f"Starting search with f-limit: {f_limit}")
        visited = {}
        new_f_limit, solution = search(Node(initial_state, None, None, 0, initial_h), 0, f_limit, [], visited)
        
        # Nếu tìm thấy lời giải
        if solution is not None:
            return {
                "solution": solution,
                "nodes_explored": nodes_explored,
                "time": time.time() - start_time,
                "depth": len(solution),
                "algorithm": "ida_star",
                "final_f_limit": f_limit
            }
        
        # Nếu không tìm thấy, tăng giới hạn f
        if new_f_limit == float('inf'):
            break
        
        f_limit = new_f_limit
        print(f"No solution found at f-limit {f_limit-1}, increasing to {f_limit}")
    
    # Không tìm thấy lời giải
    return {
        "solution": None,
        "nodes_explored": nodes_explored,
        "time": time.time() - start_time,
        "depth": None,
        "algorithm": "ida_star",
        "final_f_limit": f_limit
    }

def bidirectional_search(initial_state, max_depth=8, time_limit=60):
    """Tìm kiếm 2 chiều từ trạng thái ban đầu và trạng thái đích"""
    start_time = time.time()
    
    # Kiểm tra nếu trạng thái ban đầu đã là trạng thái đích
    if initial_state == SOLVED_STATE:
        return {
            "solution": [],
            "nodes_explored": 0,
            "time": 0,
            "depth": 0,
            "algorithm": "bidirectional"
        }
    
    # Hàm để thực hiện BFS từ một trạng thái
    def bfs_from_state(start_state, is_forward, max_depth, visited, moves_from_state):
        queue = deque([(start_state, [])])  # (trạng thái, chuỗi nước đi)
        visited[hash(start_state)] = True
        moves_from_state[hash(start_state)] = []
        
        while queue:
            state, moves = queue.popleft()
            
            # Nếu đã đạt đến độ sâu tối đa
            if len(moves) >= max_depth:
                continue
            
            for move in MOVE_NAMES:
                # Nếu đang tìm kiếm từ đích, chúng ta cần đảo ngược nước đi
                actual_move = move if is_forward else get_opposite_move(move)
                
                # Áp dụng nước đi
                next_state = apply_move(state, actual_move)
                next_state_hash = hash(next_state)
                
                if next_state_hash not in visited:
                    next_moves = moves + [actual_move]
                    visited[next_state_hash] = True
                    moves_from_state[next_state_hash] = next_moves
                    queue.append((next_state, next_moves))
        
        return visited, moves_from_state
    
    # Khởi tạo các tập đã thăm và chuỗi nước đi
    forward_visited = {}
    backward_visited = {}
    forward_moves = {}
    backward_moves = {}
    
    # Thực hiện tìm kiếm từ trạng thái ban đầu
    forward_visited, forward_moves = bfs_from_state(
        initial_state, True, max_depth // 2, forward_visited, forward_moves
    )
    
    # Thực hiện tìm kiếm từ trạng thái đích
    backward_visited, backward_moves = bfs_from_state(
        SOLVED_STATE, False, max_depth // 2, backward_visited, backward_moves
    )
    
    # Tìm điểm gặp nhau
    intersection = set(forward_visited.keys()) & set(backward_visited.keys())
    
    if not intersection:
        return {
            "solution": None,
            "nodes_explored": len(forward_visited) + len(backward_visited),
            "time": time.time() - start_time,
            "depth": None,
            "algorithm": "bidirectional"
        }
    
    # Tìm chuỗi nước đi ngắn nhất
    best_meeting_point = None
    best_path_length = float('inf')
    
    for meeting_point in intersection:
        forward_path = forward_moves[meeting_point]
        backward_path = backward_moves[meeting_point]
        path_length = len(forward_path) + len(backward_path)
        
        if path_length < best_path_length:
            best_path_length = path_length
            best_meeting_point = meeting_point
    
    # Tạo chuỗi nước đi hoàn chỉnh
    forward_path = forward_moves[best_meeting_point]
    backward_path = [get_opposite_move(move) for move in reversed(backward_moves[best_meeting_point])]
    solution = forward_path + backward_path
    
    return {
        "solution": solution,
        "nodes_explored": len(forward_visited) + len(backward_visited),
        "time": time.time() - start_time,
        "depth": len(solution),
        "algorithm": "bidirectional",
        "forward_states": len(forward_visited),
        "backward_states": len(backward_visited)
    }

def pattern_database_search(initial_state, max_depth=20, time_limit=60):
    """Tìm kiếm sử dụng cơ sở dữ liệu mẫu (chưa hoàn thiện - cần triển khai thêm)"""
    # Đây là đoạn mã giả để minh họa cách tiếp cận, cần triển khai thêm
    return ida_star_search(initial_state, max_depth, time_limit)

def solve_rubik(state, algorithm="a_star", max_depth=20, time_limit=60):
    """Wrapper function to solve Rubik's cube using different algorithms"""
    if algorithm == "a_star":
        return a_star_search(state, max_depth, time_limit)
    elif algorithm == "ida_star":
        return ida_star_search(state, max_depth, time_limit)
    elif algorithm == "bidirectional":
        return bidirectional_search(state, min(max_depth, 8), time_limit)
    elif algorithm == "pattern_database":
        return pattern_database_search(state, max_depth, time_limit)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}") 