# Thứ tự góc trong Rubik 2x2 (tương tự Rubik 3x3):
# 0=URF: Góc Trên-Phải-Trước (Up-Right-Front)
# 1=ULF: Góc Trên-Trái-Trước (Up-Left-Front)
# 2=ULB: Góc Trên-Trái-Sau (Up-Left-Back)
# 3=URB: Góc Trên-Phải-Sau (Up-Right-Back)
# 4=DRF: Góc Dưới-Phải-Trước (Down-Right-Front)
# 5=DLF: Góc Dưới-Trái-Trước (Down-Left-Front)
# 6=DLB: Góc Dưới-Trái-Sau (Down-Left-Back)
# 7=DRB: Góc Dưới-Phải-Sau (Down-Right-Back)
#
# Định hướng góc:
# 0 = đúng hướng
# 1 = xoay 1 lần theo chiều kim đồng hồ nhìn từ góc
# 2 = xoay 2 lần theo chiều kim đồng hồ nhìn từ góc

class Rubik2x2State:
    """
    Lớp quản lý trạng thái Rubik Cube 2x2.
    
    Quy ước góc (cp - corner permutation):
    0=URF, 1=ULF, 2=ULB, 3=URB, 4=DRF, 5=DLF, 6=DLB, 7=DRB
    U=Up (trên), D=Down (dưới), R=Right (phải), L=Left (trái), F=Front (trước), B=Back (sau)
    
    Định hướng góc (co - corner orientation):
    0=đúng hướng, 1=xoay theo chiều kim đồng hồ một lần, 2=xoay theo chiều kim đồng hồ hai lần
    
    Rubik 2x2 chỉ có 8 góc (không có cạnh và tâm)
    """
    def __init__(self, cp, co):
        # Sử dụng tuple thay vì list để có hiệu suất tốt hơn
        self.cp = tuple(cp)  # Corner permutation (hoán vị góc)
        self.co = tuple(co)  # Corner orientation (định hướng góc)

    def __eq__(self, other):
        if not isinstance(other, Rubik2x2State):
            return False
        return self.cp == other.cp and self.co == other.co

    def __hash__(self):
        return hash((self.cp, self.co))

    def copy(self):
        return Rubik2x2State(self.cp, self.co)
        
    def apply_move(self, move, moves_dict=None):
        """
        Áp dụng một nước đi và trả về trạng thái mới.
        - move: Nước đi cần áp dụng (e.g. 'R', 'U', 'F', etc.)
        - moves_dict: Từ điển chứa định nghĩa các nước đi, mặc định là MOVES
        """
        if moves_dict is None:
            moves_dict = MOVES_2x2
        move_def = moves_dict[move]
        
        # Lấy khối từ vị trí cũ đặt vào vị trí mới
        new_cp = tuple(self.cp[move_def['cp'][i]] for i in range(8))
        
        # Kết hợp định hướng cũ với thay đổi định hướng
        new_co = tuple((self.co[move_def['cp'][i]] + move_def['co'][i]) % 3 for i in range(8))
        
        return Rubik2x2State(new_cp, new_co)

# Trạng thái đã giải (solved)
# cp: Các góc được sắp xếp đúng vị trí (0-7)
# co: Các góc được định hướng đúng (tất cả 0)
SOLVED_STATE_2x2 = Rubik2x2State(
    tuple(range(8)),  # cp: Góc đúng vị trí
    tuple([0] * 8)    # co: Góc đúng hướng
)

# Định nghĩa các nước đi cho rubik 2x2
# Trong Rubik 2x2, chỉ có các khối góc (8 góc), không có cạnh và tâm
MOVES_2x2 = {
   
    "R'": {
        "cp": (4, 1, 2, 0, 7, 5, 6, 3),
        "co": (2, 0, 0, 1, 1, 0, 0, 2)
    },
    
 
    "R": {

        "cp": (3, 1, 2, 7, 0, 5, 6, 4),
        "co": (1, 0, 0, 2, 2, 0, 0, 1)
    },
    
    # L: Xoay mặt trái theo chiều kim đồng hồ
    "L": {
        # Vị trí 1 lấy khối từ vị trí 5, vị trí 2 lấy khối từ vị trí 1,
        # vị trí 5 lấy khối từ vị trí 6, vị trí 6 lấy khối từ vị trí 2
        "cp": (0, 5, 1, 3, 4, 6, 2, 7),
        "co": (0, 1, 2, 0, 0, 2, 1, 0)
    },
    
    # L': Xoay mặt trái ngược chiều kim đồng hồ
    "L'": {
        "cp": (0, 2, 6, 3, 4, 1, 5, 7),
        "co": (0, 2, 1, 0, 0, 1, 2, 0)
    },
    
    # F: Xoay mặt trước theo chiều kim đồng hồ
    "F": {
        "cp": (1, 5, 2, 3, 0, 4, 6, 7),
        "co": (1, 2, 0, 0, 2, 1, 0, 0)
    },
    
    # F': Xoay mặt trước ngược chiều kim đồng hồ
    "F'": {
        "cp": (4, 0, 2, 3, 5, 1, 6, 7),
        "co": (2, 1, 0, 0, 1, 2, 0, 0)
    },
    
    # B: Xoay mặt sau theo chiều kim đồng hồ
    "B": {
        "cp": (0, 1, 3, 7, 4, 5, 2, 6),
        "co": (0, 0, 1, 2, 0, 0, 2, 1)
    },
    
    # B': Xoay mặt sau ngược chiều kim đồng hồ
    "B'": {
        "cp": (0, 1, 6, 2, 4, 5, 7, 3),
        "co": (0, 0, 2, 1, 0, 0, 1, 2)
    },
    
    # U: Xoay mặt trên theo chiều kim đồng hồ
    "U": {
        "cp": (3, 0, 1, 2, 4, 5, 6, 7),
        "co": (0, 0, 0, 0, 0, 0, 0, 0)
    },
    
    # U': Xoay mặt trên ngược chiều kim đồng hồ
    "U'": {
        "cp": (1, 2, 3, 0, 4, 5, 6, 7),
        "co": (0, 0, 0, 0, 0, 0, 0, 0)
    },
    
    # D: Xoay mặt dưới theo chiều kim đồng hồ
    "D": {
        "cp": (0, 1, 2, 3, 5, 6, 7, 4),
        "co": (0, 0, 0, 0, 0, 0, 0, 0)
    },
    
    # D': Xoay mặt dưới ngược chiều kim đồng hồ
    "D'": {
        "cp": (0, 1, 2, 3, 7, 4, 5, 6),
        "co": (0, 0, 0, 0, 0, 0, 0, 0)
    }
}

MOVE_NAMES = list(MOVES_2x2.keys())

def calculate_parity(perm):
    """Tính dấu hoán vị (chẵn: 0, lẻ: 1)"""
    # Không cần thay đổi vì tuple có thể duyệt như list
    inversions = 0
    for i in range(len(perm)):
        for j in range(i + 1, len(perm)):
            if perm[i] > perm[j]:
                inversions += 1
    return inversions % 2

def heuristic_2x2(state):
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