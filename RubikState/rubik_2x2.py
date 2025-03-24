class Rubik2x2State:
    def __init__(self, cp, co):
        # Chuyển đổi tất cả các danh sách thành tuple để tăng hiệu suất
        self.cp = tuple(cp)  # Hoán vị góc (corner permutation)
        self.co = tuple(co)  # Định hướng góc (corner orientation)

    def __eq__(self, other):
        # So sánh tuple trực tiếp, nhanh hơn list
        return self.cp == other.cp and self.co == other.co

    def __hash__(self):
        # Đơn giản hơn vì đã dùng tuple, không cần chuyển đổi
        return hash((self.cp, self.co))

    def copy(self):
        # Không cần .copy() cho tuple vì tuple là immutable
        return Rubik2x2State(self.cp, self.co)

# Trạng thái mục tiêu - sử dụng tuple thay vì list
SOLVED_STATE = Rubik2x2State(
    cp=(0, 1, 2, 3, 4, 5, 6, 7),  # Hoán vị góc ban đầu
    co=(0, 0, 0, 0, 0, 0, 0, 0)   # Định hướng góc ban đầu
)

# Định nghĩa các nước đi cho rubik 2x2
# Mặc dù rubik 2x2 có cấu trúc đơn giản hơn, chúng ta vẫn giữ nguyên các định nghĩa
# về góc để đảm bảo tính nhất quán với mô hình 3x3
MOVES = {
    # Mặt phải (R)
    "R": {
        "cp_perm": [0, 1, 6, 3, 4, 5, 2, 7],  # URF->DRF->DRB->URB->URF
        "co_change": [0, 0, 1, 0, 0, 0, 2, 0],  # Định hướng thay đổi
    },
    # Mặt trái (L)
    "L": {
        "cp_perm": [0, 1, 2, 3, 5, 4, 6, 7],  # ULF->ULB->DLB->DLF->ULF
        "co_change": [0, 0, 0, 0, 2, 1, 0, 0],
    },
    # Mặt trên (U)
    "U": {
        "cp_perm": [3, 0, 1, 2, 4, 5, 6, 7],  # URF->ULF->ULB->URB->URF
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
    },
    # Mặt dưới (D)
    "D": {
        "cp_perm": [0, 1, 2, 3, 7, 4, 5, 6],  # DRF->DLF->DLB->DRB->DRF
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
    },
    # Mặt trước (F)
    "F": {
        "cp_perm": [1, 5, 2, 3, 0, 4, 6, 7],  # URF->DLF->ULF->URF
        "co_change": [1, 2, 0, 0, 2, 1, 0, 0],
    },
    # Mặt sau (B)
    "B": {
        "cp_perm": [0, 1, 2, 7, 4, 5, 3, 6],  # URB->DRB->DLB->ULB->URB
        "co_change": [0, 0, 0, 1, 0, 0, 2, 2],
    },
    # Nước đi ngược
    "R'": {
        "cp_perm": [0, 1, 6, 3, 4, 5, 2, 7],  # URB->URF->DRF->DRB->URB
        "co_change": [0, 0, 2, 0, 0, 0, 1, 0],
    },
    "L'": {
        "cp_perm": [0, 1, 2, 3, 5, 4, 6, 7],  # ULF->DLF->DLB->ULB->ULF
        "co_change": [0, 0, 0, 0, 1, 2, 0, 0],
    },
    "U'": {
        "cp_perm": [1, 2, 3, 0, 4, 5, 6, 7],  # URF->URB->ULB->ULF->URF
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
    },
    "D'": {
        "cp_perm": [0, 1, 2, 3, 5, 6, 7, 4],  # DRF->DRB->DLB->DLF->DRF
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
    },
    "F'": {
        "cp_perm": [4, 0, 2, 3, 5, 1, 6, 7],  # URF->ULF->DLF->DRF->URF
        "co_change": [2, 1, 0, 0, 1, 2, 0, 0],
    },
    "B'": {
        "cp_perm": [0, 1, 2, 6, 4, 5, 7, 3],  # URB->ULB->DLB->DRB->URB
        "co_change": [0, 0, 0, 2, 0, 0, 1, 2],
    },
    # Nước đi 180 độ (2 lần)
    "R2": {
        "cp_perm": [0, 1, 2, 6, 4, 5, 3, 7],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
    },
    "L2": {
        "cp_perm": [0, 1, 2, 3, 4, 5, 6, 7],  # Về vị trí ban đầu nhưng hoán vị
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
    },
    "U2": {
        "cp_perm": [2, 3, 0, 1, 4, 5, 6, 7],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
    },
    "D2": {
        "cp_perm": [0, 1, 2, 3, 6, 7, 4, 5],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
    },
    "F2": {
        "cp_perm": [5, 4, 2, 3, 1, 0, 6, 7],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
    },
    "B2": {
        "cp_perm": [0, 1, 2, 7, 4, 5, 6, 3],
        "co_change": [0, 0, 0, 0, 0, 0, 0, 0],
    }
}

MOVE_NAMES = list(MOVES.keys())

# Hàm áp dụng một nước đi
def apply_move(state, move):
    move_data = MOVES[move]
    
    # Tạo tuple mới trực tiếp, bỏ qua bước tạo list
    new_cp = tuple(state.cp[move_data["cp_perm"][i]] for i in range(8))
    new_co = tuple((state.co[move_data["cp_perm"][i]] + move_data["co_change"][i]) % 3 for i in range(8))
    
    return Rubik2x2State(new_cp, new_co)

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
    
    corner_total = corner_misplaced + corner_misoriented
    h_corner = corner_total // 4
    
    # Tính toán dấu hoán vị
    corner_parity = calculate_parity(state.cp)
    
    # Tính toán định hướng tổng
    corner_orient_sum = sum(state.co) % 3
    h_orient = 1 if corner_orient_sum != 0 else 0
    
    # Lấy giá trị lớn nhất
    return max(h_corner, corner_parity, h_orient)