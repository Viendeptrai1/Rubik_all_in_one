class RubikState:
    def __init__(self, cp, co, ep, eo):
        # Chuyển đổi tất cả các danh sách thành tuple để tăng hiệu suất
        self.cp = tuple(cp)  # Hoán vị góc
        self.co = tuple(co)  # Định hướng góc
        self.ep = tuple(ep)  # Hoán vị cạnh
        self.eo = tuple(eo)  # Định hướng cạnh

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
        "cp_perm": [3, 1, 2, 6, 0, 5, 4, 7],  # urf -> urb -> drb -> drf -> urf
        "co_change": [1, 0, 0, 2, 2, 0, 1, 0],  # Định hướng thay đổi
        "ep_perm": [11, 1, 2, 3, 8, 5, 6, 7, 4, 9, 10, 0],  # ur -> rb -> dr -> fr -> ur
        "eo_change": [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1]
    },
    "L": {
        "cp_perm": [0, 1, 5, 3, 4, 7, 6, 2],  # ulf -> dlb -> dlf -> ulf
        "co_change": [0, 0, 1, 0, 0, 2, 0, 1],
        "ep_perm": [0, 1, 9, 3, 4, 5, 10, 7, 8, 6, 2, 11],  # ul -> fl -> dl -> bl -> ul
        "eo_change": [0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0]
    },
    "U": {
        "cp_perm": [1, 2, 3, 0, 4, 5, 6, 7],  # urf -> ufr -> ulf -> ubr -> urf
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [1, 2, 3, 0, 4, 5, 6, 7, 8, 9, 10, 11],  # ur -> uf -> ul -> ub -> ur
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "D": {
        "cp_perm": [0, 1, 2, 3, 7, 4, 5, 6],  # dfr -> dlf -> dlb -> dbr -> dfr
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11],  # dr -> df -> dl -> db -> dr
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "F": {
        "cp_perm": [1, 4, 2, 3, 7, 5, 6, 0],  # urf -> ufr -> dfr -> dlf -> urf
        "co_change": [1, 2, 0, 0, 1, 0, 0, 2],
        "ep_perm": [0, 8, 2, 3, 4, 9, 6, 7, 5, 1, 10, 11],  # uf -> fr -> df -> fl -> uf
        "eo_change": [0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0]
    },
    "B": {
        "cp_perm": [0, 1, 3, 6, 4, 2, 5, 7],  # ubr -> dbr -> dlb -> ulf -> ubr
        "co_change": [0, 0, 2, 1, 0, 1, 2, 0],
        "ep_perm": [0, 1, 2, 10, 4, 5, 6, 11, 8, 9, 7, 3],  # ub -> bl -> db -> br -> ub
        "eo_change": [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1]
    },
    "R'": {
        "cp_perm": [4, 1, 2, 0, 6, 5, 3, 7],
        "co_change": [2, 0, 0, 1, 1, 0, 2, 0],
        "ep_perm": [0, 1, 2, 3, 8, 5, 6, 7, 4, 9, 10, 11],
        "eo_change": [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1]
    },
    "L'": {
        "cp_perm": [0, 1, 7, 3, 4, 2, 6, 5],
        "co_change": [0, 0, 2, 0, 0, 1, 0, 2],
        "ep_perm": [0, 1, 10, 3, 4, 5, 9, 7, 8, 2, 6, 11],
        "eo_change": [0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0]
    },
    "U'": {
        "cp_perm": [3, 0, 1, 2, 4, 5, 6, 7],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "B'": {
        "cp_perm": [0, 1, 5, 2, 4, 6, 3, 7],
        "co_change": [0, 0, 1, 2, 0, 2, 1, 0],
        "ep_perm": [0, 1, 2, 11, 4, 5, 6, 10, 8, 9, 3, 7],
        "eo_change": [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1]
    },
    "D'": {
        "cp_perm": [0, 1, 2, 3, 5, 6, 7, 4],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [0, 1, 2, 3, 7, 4, 5, 6, 8, 9, 10, 11],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "F'": {
        "cp_perm": [7, 0, 2, 3, 1, 5, 6, 4],
        "co_change": [2, 1, 0, 0, 2, 0, 0, 1],
        "ep_perm": [0, 9, 2, 3, 4, 8, 6, 7, 1, 5, 10, 11],
        "eo_change": [0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0]
    },
    "R2": {
        "cp_perm": [6, 1, 2, 4, 3, 5, 0, 7],  # Thực hiện R hai lần
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],  # Tổng thay đổi định hướng là 0
        "ep_perm": [4, 1, 2, 3, 0, 5, 6, 7, 11, 9, 10, 8],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },

    # Mặt trái (L)
    
    "L2": {
        "cp_perm": [0, 1, 5, 3, 4, 7, 6, 2],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [0, 1, 6, 3, 4, 5, 2, 7, 8, 10, 9, 11],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },

    # Mặt trên (U)
    
    "U2": {
        "cp_perm": [2, 3, 0, 1, 4, 5, 6, 7],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [2, 3, 0, 1, 4, 5, 6, 7, 8, 9, 10, 11],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },

    # Mặt dưới (D)
    
    
    "D2": {
        "cp_perm": [0, 1, 2, 3, 6, 7, 4, 5],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [0, 1, 2, 3, 6, 7, 4, 5, 8, 9, 10, 11],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },

    # Mặt trước (F)
    
    "F2": {
        "cp_perm": [4, 7, 2, 3, 0, 5, 6, 1],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [0, 5, 2, 3, 4, 1, 6, 7, 9, 8, 10, 11],
        "eo_change": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },

    # Mặt sau (B)
    
    
    "B2": {
        "cp_perm": [0, 1, 6, 5, 4, 3, 2, 7],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
        "ep_perm": [0, 1, 2, 7, 4, 5, 6, 3, 8, 9, 11, 10],
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