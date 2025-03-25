class RubikState:
    def __init__(self, cp, co, ep, eo):
        # Chuyển đổi tất cả các danh sách thành tuple để tăng hiệu suất
        self.cp = tuple(cp)  # Hoán vị góc (corner permutation)
        self.co = tuple(co)  # Định hướng góc (corner orientation)
        self.ep = tuple(ep)  # Hoán vị cạnh (edge permutation)
        self.eo = tuple(eo)  # Định hướng cạnh (edge orientation)

    def __eq__(self, other):
        # So sánh tuple trực tiếp, nhanh hơn list
        return (self.cp == other.cp and self.co == other.co and
                self.ep == other.ep and self.eo == other.eo)

    def __hash__(self):
        # Đơn giản hơn vì đã dùng tuple, không cần chuyển đổi
        return hash((self.cp, self.co, self.ep, self.eo))

    def copy(self):
        # Không cần .copy() cho tuple vì tuple là immutable
        return RubikState(self.cp, self.co, self.ep, self.eo)

# Trạng thái mục tiêu - sử dụng tuple thay vì list
SOLVED_STATE = RubikState(
    cp=(0, 1, 2, 3, 4, 5, 6, 7),
    co=(0, 0, 0, 0, 0, 0, 0, 0),
    ep=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
    eo=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
)

# Định nghĩa các nước đi
MOVES = {
    # Mặt phải (R)
    "R": {
        "cp_perm": [0, 1, 2, 7, 4, 5, 3, 6],  # urf -> urb -> drb -> drf -> urf
        "co_change": [0, 0, 0, 1, 0, 0, 2, 1],  # Định hướng thay đổi
        "ep_perm": [0, 1, 2, 3, 4, 5, 10, 7, 8, 9, 6, 11],  # ur -> br -> dr -> fr -> ur
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "L": {
        "cp_perm": [4, 1, 2, 3, 7, 0, 6, 5],  # ulf -> dlf -> dlb -> ulf
        "co_change": [2, 0, 0, 0, 1, 1, 0, 2],
        "ep_perm": [0, 1, 2, 3, 4, 8, 6, 7, 9, 5, 10, 11],  # ul -> fl -> dl -> bl -> ul
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "U": {
        "cp_perm": [3, 0, 1, 2, 4, 5, 6, 7],  # urf -> ufr -> ulf -> ubr -> urf
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11],  # ur -> uf -> ul -> ub -> ur
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "D": {
        "cp_perm": [0, 1, 2, 3, 5, 6, 7, 4],  # dfr -> dlf -> dlb -> dbr -> dfr
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [0, 1, 2, 3, 7, 4, 5, 6, 8, 9, 10, 11],  # dr -> df -> dl -> db -> dr
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "F": {
        "cp_perm": [0, 7, 2, 3, 4, 5, 1, 6],  # ufr -> dfr -> dlf -> ufr
        "co_change": [0, 1, 0, 0, 0, 0, 2, 1],
        "ep_perm": [0, 4, 2, 3, 8, 5, 6, 7, 1, 9, 10, 11],  # uf -> fr -> df -> fl -> uf
        "eo_change": [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    },
    "B": {
        "cp_perm": [5, 1, 2, 0, 4, 6, 3, 7],  # ubr -> ulb -> dlb -> dbr -> ubr
        "co_change": [1, 0, 0, 2, 0, 1, 0, 2],
        "ep_perm": [2, 1, 6, 3, 4, 5, 10, 7, 8, 9, 11, 0],  # ub -> bl -> db -> br -> ub
        "eo_change": [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    },
    "R'": {
        "cp_perm": [0, 1, 2, 6, 4, 5, 7, 3],
        "co_change": [0, 0, 0, 2, 0, 0, 1, 1],
        "ep_perm": [0, 1, 2, 3, 4, 5, 10, 7, 8, 9, 6, 11],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "L'": {
        "cp_perm": [5, 1, 2, 3, 0, 7, 6, 4],
        "co_change": [1, 0, 0, 0, 2, 2, 0, 1],
        "ep_perm": [0, 1, 2, 3, 4, 9, 6, 7, 5, 8, 10, 11],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "U'": {
        "cp_perm": [1, 2, 3, 0, 4, 5, 6, 7],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [1, 2, 3, 0, 4, 5, 6, 7, 8, 9, 10, 11],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "D'": {
        "cp_perm": [0, 1, 2, 3, 7, 4, 5, 6],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "F'": {
        "cp_perm": [0, 6, 2, 3, 4, 5, 7, 1],
        "co_change": [0, 2, 0, 0, 0, 0, 1, 1],
        "ep_perm": [0, 8, 2, 3, 9, 5, 6, 7, 4, 1, 10, 11],
        "eo_change": [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    },
    "B'": {
        "cp_perm": [3, 1, 2, 6, 4, 0, 5, 7],
        "co_change": [2, 0, 0, 1, 0, 2, 0, 1],
        "ep_perm": [11, 1, 2, 3, 4, 5, 6, 10, 8, 9, 0, 7],
        "eo_change": [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1]
    },
    "R2": {
        "cp_perm": [0, 1, 2, 6, 4, 5, 7, 3],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [0, 1, 2, 3, 4, 5, 6, 7, 10, 9, 8, 11],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "L2": {
        "cp_perm": [7, 1, 2, 3, 5, 4, 6, 0],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [0, 1, 2, 3, 4, 9, 6, 7, 5, 8, 10, 11],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "U2": {
        "cp_perm": [2, 3, 0, 1, 4, 5, 6, 7],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [2, 3, 0, 1, 4, 5, 6, 7, 8, 9, 10, 11],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "D2": {
        "cp_perm": [0, 1, 2, 3, 6, 7, 4, 5],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [0, 1, 2, 3, 6, 7, 4, 5, 8, 9, 10, 11],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "F2": {
        "cp_perm": [0, 6, 2, 3, 4, 5, 7, 1],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [0, 9, 2, 3, 1, 5, 6, 7, 8, 4, 10, 11],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "B2": {
        "cp_perm": [5, 1, 2, 6, 4, 3, 0, 7],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [7, 1, 2, 10, 4, 5, 6, 3, 8, 9, 11, 0],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    }
}

MOVE_NAMES = list(MOVES.keys())

# Hàm áp dụng một nước đi
def apply_move(state, move):
    move_data = MOVES[move]
    
    # Tạo tuple mới trực tiếp, bỏ qua bước tạo list
    new_cp = tuple(state.cp[move_data["cp_perm"][i]] for i in range(8))
    new_co = tuple((state.co[move_data["cp_perm"][i]] + move_data["co_change"][i]) % 3 for i in range(8))
    new_ep = tuple(state.ep[move_data["ep_perm"][i]] for i in range(12))
    new_eo = tuple((state.eo[move_data["ep_perm"][i]] + move_data["eo_change"][i]) % 2 for i in range(12))
    
    return RubikState(new_cp, new_co, new_ep, new_eo)

def calculate_parity(perm):
    """Tính dấu hoán vị (chẵn: 0, lẻ: 1)"""
    # Không cần thay đổi vì tuple có thể duyệt như list
    inversions = 0
    for i in range(len(perm)):
        for j in range(i + 1, len(perm)):
            if perm[i] > perm[j]:
                inversions += 1
    return inversions % 2

def heuristic(state):
    # Tối ưu hóa bằng cách kết hợp các vòng lặp
    corner_misplaced = corner_misoriented = 0
    for i in range(8):
        if state.cp[i] != i:
            corner_misplaced += 1
        if state.co[i] != 0:
            corner_misoriented += 1
    
    edge_misplaced = edge_misoriented = 0
    for i in range(12):
        if state.ep[i] != i:
            edge_misplaced += 1
        if state.eo[i] != 0:
            edge_misoriented += 1
    
    corner_total = corner_misplaced + corner_misoriented
    h_corner = corner_total // 4
    
    edge_total = edge_misplaced + edge_misoriented
    h_edge = edge_total // 4
    
    # Tính toán dấu hoán vị
    corner_parity = calculate_parity(state.cp)
    edge_parity = calculate_parity(state.ep)
    h_parity = 1 if corner_parity != edge_parity else 0
    
    # Tính toán định hướng tổng
    corner_orient_sum = sum(state.co) % 3
    edge_orient_sum = sum(state.eo) % 2
    h_orient = 1 if corner_orient_sum != 0 or edge_orient_sum != 0 else 0
    
    # Lấy giá trị lớn nhất
    return max(h_corner, h_edge, h_parity, h_orient)

def generate_random_state():
    """Tạo một trạng thái Rubik ngẫu nhiên hợp lệ"""
    import random
    
    # Tạo hoán vị góc ngẫu nhiên
    cp = list(range(8))
    random.shuffle(cp)
    
    # Tạo định hướng góc ngẫu nhiên (tổng định hướng phải chia hết cho 3)
    co = [random.randint(0, 2) for _ in range(7)]
    co_sum = sum(co) % 3
    co.append((3 - co_sum) % 3)
    
    # Tạo hoán vị cạnh ngẫu nhiên
    ep = list(range(12))
    random.shuffle(ep)
    
    # Tạo định hướng cạnh ngẫu nhiên (tổng định hướng phải chia hết cho 2)
    eo = [random.randint(0, 1) for _ in range(11)]
    eo_sum = sum(eo) % 2
    eo.append((2 - eo_sum) % 2)
    
    # Đảm bảo tính chẵn lẻ của hoán vị góc và cạnh là như nhau
    if calculate_parity(cp) != calculate_parity(ep):
        # Đổi chỗ hai cạnh để thay đổi tính chẵn lẻ
        ep[0], ep[1] = ep[1], ep[0]
    
    return RubikState(cp, co, ep, eo)

def is_solved(state):
    """Kiểm tra xem khối Rubik đã được giải chưa"""
    return state == SOLVED_STATE

def cube_to_state(rubik_cube):
    """Chuyển đổi từ mô hình RubikCube sang RubikState"""
    # Thực hiện chuyển đổi từ mô hình 3D sang trạng thái hoán vị/định hướng
    # Hàm này cần được triển khai để tương thích với cấu trúc RubikCube hiện tại
    pass

def state_to_cube(state, rubik_cube=None):
    """Chuyển đổi từ RubikState sang mô hình RubikCube"""
    # Thực hiện chuyển đổi từ trạng thái hoán vị/định hướng sang mô hình 3D
    # Hàm này cần được triển khai để tương thích với cấu trúc RubikCube hiện tại
    pass 