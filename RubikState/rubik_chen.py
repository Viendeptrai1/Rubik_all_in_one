# Thứ tự góc: 0=URF, 1=ULF, 2=ULB, 3=URB, 4=DRF, 5=DLF, 6=DLB, 7=DRB
# Định hướng góc: 0=đúng hướng, 1=xoay 1 lần theo chiều kim đồng hồ, 2=xoay 2 lần
# Thứ tự cạnh: 0=UR, 1=UF, 2=UL, 3=UB, 4=DR, 5=DF, 6=DL, 7=DB, 8=FR, 9=FL, 10=BL, 11=BR
# Định hướng cạnh: 0=đúng hướng, 1=lật ngược
# U là trắng, D là vàng, F là đỏ, B là cam, L là xanh lá, R là xanh dương
class RubikState:
    """
    Lớp quản lý trạng thái Rubik Cube 3x3.
    
    Quy ước góc (cp - corner permutation):
    0=URF, 1=ULF, 2=ULB, 3=URB, 4=DRF, 5=DLF, 6=DLB, 7=DRB
    U=Up (trên), D=Down (dưới), R=Right (phải), L=Left (trái), F=Front (trước), B=Back (sau)
    
    Định hướng góc (co - corner orientation):
    0=đúng hướng, 1=xoay theo chiều kim đồng hồ một lần, 2=xoay theo chiều kim đồng hồ hai lần
    
    Quy ước cạnh (ep - edge permutation):
    0=UR, 1=UF, 2=UL, 3=UB, 4=DR, 5=DF, 6=DL, 7=DB, 8=FR, 9=FL, 10=BL, 11=BR
    
    Định hướng cạnh (eo - edge orientation):
    0=đúng hướng, 1=lật ngược
    """
    def __init__(self, cp, co, ep, eo):
        # Sử dụng tuple thay vì list để có hiệu suất tốt hơn
        self.cp = tuple(cp)  # Corner permutation (hoán vị góc)
        self.co = tuple(co)  # Corner orientation (định hướng góc)
        self.ep = tuple(ep)  # Edge permutation (hoán vị cạnh)
        self.eo = tuple(eo)  # Edge orientation (định hướng cạnh)

    def __eq__(self, other):
        if not isinstance(other, RubikState):
            return False
        return (self.cp == other.cp and self.co == other.co and
                self.ep == other.ep and self.eo == other.eo)

    def __hash__(self):
        return hash((self.cp, self.co, self.ep, self.eo))

    def copy(self):
        return RubikState(self.cp, self.co, self.ep, self.eo)

    def apply_move(self, move, moves_dict=None):
        if moves_dict is None:
            moves_dict = MOVES_3x3
        move_def = moves_dict[move]
        new_cp = tuple(self.cp[p] for p in move_def['cp'])
        new_co = tuple((self.co[p] + o) % 3 for p, o in zip(move_def['cp'], move_def['co']))
        new_ep = tuple(self.ep[p] for p in move_def['ep'])
        new_eo = tuple((self.eo[p] + o) % 2 for p, o in zip(move_def['ep'], move_def['eo']))
        return RubikState(new_cp, new_co, new_ep, new_eo)

# Trạng thái đã giải (solved)
# cp: Các góc được sắp xếp đúng vị trí (0-7)
# co: Các góc được định hướng đúng (tất cả 0)
# ep: Các cạnh được sắp xếp đúng vị trí (0-11)
# eo: Các cạnh được định hướng đúng (tất cả 0)
SOLVED_STATE_3x3 = RubikState(
    tuple(range(8)),  # cp: Góc đúng vị trí
    tuple([0] * 8),   # co: Góc đúng hướng
    tuple(range(12)), # ep: Cạnh đúng vị trí
    tuple([0] * 12)   # eo: Cạnh đúng hướng
)

# Dictionary chứa các nước đi và tác động của chúng đến trạng thái
# Mỗi nước đi định nghĩa:
# - cp: Hoán vị góc (vị trí mới của mỗi góc sau khi xoay)
# - co: Thay đổi hướng góc (0=không đổi, 1=xoay CW, 2=xoay CCW)
# - ep: Hoán vị cạnh (vị trí mới của mỗi cạnh sau khi xoay)
# - eo: Thay đổi hướng cạnh (0=không đổi, 1=lật ngược)
MOVES_3x3 = {
    # === Phép xoay mặt U (Up - trên) 90 độ CW ===
    'U': {
        # Góc: 0=URF, 1=ULF, 2=ULB, 3=URB | Di chuyển: 0->3, 1->0, 2->1, 3->2
        'cp': (1, 2, 3, 0, 4, 5, 6, 7), 
        # Hướng góc không đổi khi xoay U
        'co': (0, 0, 0, 0, 0, 0, 0, 0),
        # Cạnh: 0=UR, 1=UF, 2=UL, 3=UB | Di chuyển: 0->3, 1->0, 2->1, 3->2
        'ep': (1, 2, 3, 0, 4, 5, 6, 7, 8, 9, 10, 11),
        # Hướng cạnh không đổi khi xoay U
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },

    # === Phép xoay mặt R (Right - phải) 90 độ CW ===
    'R': {
        # Góc: 0=URF, 3=URB, 7=DRB, 4=DRF | Di chuyển: 0->4, 3->0, 7->3, 4->7
        'cp': (3, 1, 2, 7, 0, 5, 6, 4),
        # URF(+1), URB(+2), DRB(+1), DRF(+2) -> Thay đổi hướng tại vị trí mới
        'co': (1, 0, 0, 2, 2, 0, 0, 1), 
        # Cạnh: 0=UR, 11=BR, 7=DB -> 4=DR, 8=FR | Di chuyển: 0->8, 11->0, 4->11, 8->4 (Chú ý: DB(7) không thuộc mặt R)
        # Cạnh bị ảnh hưởng: 0=UR, 8=FR, 4=DR, 11=BR | Di chuyển: 0->8, 8->4, 4->11, 11->0
        'ep': (11, 1, 2, 3, 8, 5, 6, 7, 4, 9, 10, 0),
        # Hướng cạnh không đổi khi xoay R
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },

    # === Phép xoay mặt F (Front - trước) 90 độ CW ===
    'F': {
        # Góc: 0=URF, 1=ULF, 5=DLF, 4=DRF | Di chuyển: 0->5, 1->0, 5->4, 4->1
        'cp': (1, 5, 2, 3, 0, 4, 6, 7),
        # URF(+1), ULF(+2), DLF(+1), DRF(+2) -> Thay đổi hướng tại vị trí mới
        'co': (1, 2, 0, 0, 2, 1, 0, 0),
        # Cạnh: 1=UF, 9=FL, 5=DF, 8=FR | Di chuyển: 1->9, 9->5, 5->8, 8->1
        'ep': (0, 8, 2, 3, 4, 9, 6, 7, 1, 5, 10, 11),
        # 4 cạnh trên mặt F đều bị lật
        'eo': (0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0)
    },

    # === Phép xoay mặt D (Down - dưới) 90 độ CW ===
    'D': {
        # Góc: 4=DRF, 5=DLF, 6=DLB, 7=DRB | Di chuyển: 4->7, 5->4, 6->5, 7->6
        'cp': (0, 1, 2, 3, 5, 6, 7, 4),
        # Hướng góc không đổi khi xoay D
        'co': (0, 0, 0, 0, 0, 0, 0, 0),
        # Cạnh: 4=DR, 5=DF, 6=DL, 7=DB | Di chuyển: 4->7, 5->4, 6->5, 7->6
        'ep': (0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11),
        # Hướng cạnh không đổi khi xoay D
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },

    # === Phép xoay mặt L (Left - trái) 90 độ CW ===
    'L': {
        # Góc: 1=ULF, 2=ULB, 6=DLB, 5=DLF | Di chuyển: 1->6, 2->1, 6->5, 5->2
        'cp': (0, 2, 6, 3, 4, 1, 5, 7),
        # ULF(+2), ULB(+1), DLB(+2), DLF(+1) -> Thay đổi hướng tại vị trí mới
        'co': (0, 2, 1, 0, 0, 1, 2, 0),
        # Cạnh: 2=UL, 10=BL, 6=DL, 9=FL | Di chuyển: 2->10, 10->6, 6->9, 9->2
        'ep': (0, 1, 9, 3, 4, 5, 10, 7, 8, 6, 2, 11),
        # Hướng cạnh không đổi khi xoay L
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },

    # === Phép xoay mặt B (Back - sau) 90 độ CW ===
    'B': {
        # Góc: 2=ULB, 3=URB, 7=DRB, 6=DLB | Di chuyển: 2->7, 3->2, 7->6, 6->3
        'cp': (0, 1, 3, 6, 4, 5, 2, 7),
         # ULB(+2), URB(+1), DRB(+2), DLB(+1) -> Thay đổi hướng tại vị trí mới
        'co': (0, 0, 2, 1, 0, 0, 1, 2),
        # Cạnh: 3=UB, 11=BR, 7=DB, 10=BL | Di chuyển: 3->11, 11->7, 7->10, 10->3
        'ep': (0, 1, 2, 10, 4, 5, 6, 11, 8, 9, 7, 3),
        # 4 cạnh trên mặt B đều bị lật
        'eo': (0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1)
    },
    # === Phép xoay ngược chiều (CCW - prime) ===
    "U'": { 
        'cp': (3, 0, 1, 2, 4, 5, 6, 7), 
        'co': (0, 0, 0, 0, 0, 0, 0, 0),
        'ep': (3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11),
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },
    "R'": {
        'cp': (4, 1, 2, 0, 7, 5, 6, 3),
        'co': (1, 0, 0, 2, 2, 0, 0, 1), # (-co_R[p_inv[k]]) % 3
        'ep': (11, 1, 2, 3, 8, 5, 6, 7, 4, 9, 10, 0), # Nghịch đảo của ep_R
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },
     "F'": {
        'cp': (4, 0, 2, 3, 5, 1, 6, 7),
        'co': (1, 2, 0, 0, 2, 1, 0, 0), # (-co_F[p_inv[k]]) % 3
        'ep': (0, 8, 2, 3, 4, 9, 6, 7, 1, 5, 10, 11), # Nghịch đảo của ep_F
        'eo': (0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0)  # (-eo_F[p_inv[k]]) % 2
    },
     "D'": {
        'cp': (0, 1, 2, 3, 7, 4, 5, 6),
        'co': (0, 0, 0, 0, 0, 0, 0, 0),
        'ep': (0, 1, 2, 3, 7, 4, 5, 6, 8, 9, 10, 11), # Nghịch đảo của ep_D
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },
     "L'": {
        'cp': (0, 5, 1, 3, 4, 6, 2, 7),
        'co': (0, 2, 1, 0, 0, 1, 2, 0), # (-co_L[p_inv[k]]) % 3
        'ep': (0, 1, 10, 3, 4, 5, 9, 7, 8, 2, 6, 11), # Nghịch đảo của ep_L
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },
     "B'": {
        'cp': (0, 1, 6, 2, 4, 5, 3, 7),
        'co': (0, 0, 2, 1, 0, 0, 1, 2), # (-co_B[p_inv[k]]) % 3
        'ep': (0, 1, 2, 11, 4, 5, 6, 10, 8, 9, 3, 7), # Nghịch đảo của ep_B
        'eo': (0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1)  # (-eo_B[p_inv[k]]) % 2
    }
}

# Danh sách tên các nước đi 
MOVE_NAMES = list(MOVES_3x3.keys())

def calculate_parity(perm):
    """Tính dấu hoán vị (chẵn: 0, lẻ: 1)"""
    # Không cần thay đổi vì tuple có thể duyệt như list
    inversions = 0
    for i in range(len(perm)):
        for j in range(i + 1, len(perm)):
            if perm[i] > perm[j]:
                inversions += 1
    return inversions % 2

def heuristic_3x3(state):
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