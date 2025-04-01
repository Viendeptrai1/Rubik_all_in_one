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
        """
        Áp dụng một nước đi và trả về trạng thái mới.
        SỬA LẠI THEO LOGIC GIỐNG RUBIK 2X2 (PUSH)
        
        Args:
            move: Nước đi cần áp dụng (e.g. 'R', 'U', 'F', etc.)
            moves_dict: Từ điển chứa định nghĩa các nước đi, mặc định là MOVES_3x3
            
        Returns:
            RubikState: Trạng thái mới sau khi áp dụng nước đi
        """
        if moves_dict is None:
            moves_dict = MOVES_3x3
        
        # Lấy định nghĩa phép xoay
        if move not in moves_dict:
            raise ValueError(f"Nước đi không hợp lệ: {move}")
        move_def = moves_dict[move]
        
        # === Áp dụng hoán vị và định hướng GÓC (giống 2x2) ===
        new_cp = [0] * 8
        new_co = [0] * 8
        for i in range(8):
            source_corner_index = move_def['cp'][i]
            new_cp[i] = self.cp[source_corner_index]
            new_co[i] = (self.co[source_corner_index] + move_def['co'][i]) % 3
        
        # === Áp dụng hoán vị và định hướng CẠNH (tương tự logic góc) ===
        new_ep = [0] * 12
        new_eo = [0] * 12
        for i in range(12):
            source_edge_index = move_def['ep'][i]
            new_ep[i] = self.ep[source_edge_index]
            new_eo[i] = (self.eo[source_edge_index] + move_def['eo'][i]) % 2
        
        # Chuyển sang tuple để tối ưu hiệu suất
        return RubikState(tuple(new_cp), tuple(new_co), tuple(new_ep), tuple(new_eo))

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

# ĐỊNH NGHĨA CHUẨN VERIFIED CHO MOVES_3x3
MOVES_3x3 = {
    # === Phép xoay mặt U (Up - trên) 90 độ CW ===
    'U': {
        'cp': (3, 0, 1, 2, 4, 5, 6, 7), # Góc: URF->URB, ULF->URF, ULB->ULF, URB->ULB
        'co': (0, 0, 0, 0, 0, 0, 0, 0), # Orientation doesn't change for U/D moves
        'ep': (3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11), # Cạnh: UR->UB, UF->UR, UL->UF, UB->UL
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), # Orientation doesn't change for U/D moves
    },
    # === Phép xoay mặt R (Right - phải) 90 độ CW ===
    'R': {
        'cp': (4, 1, 2, 0, 7, 5, 6, 3), # Góc: URF->DRF, URB->URF, DRB->URB, DRF->DRB
        'co': (2, 0, 0, 1, 1, 0, 0, 2), # Orientation changes: +2, +1, +2, +1 clockwise twist relative to face normal
        'ep': (8, 1, 2, 3, 11, 5, 6, 7, 0, 9, 10, 4), # Cạnh: UR->FR, FR->DR, DR->BR, BR->UR
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), # Orientation doesn't change for R/L moves
    },
    # === Phép xoay mặt F (Front - trước) 90 độ CW ===
    'F': {
        'cp': (1, 5, 2, 3, 0, 4, 6, 7), # Góc: URF->ULF, ULF->DLF, DLF->DRF, DRF->URF
        'co': (1, 2, 0, 0, 2, 1, 0, 0), # Orientation changes: +1, +2, +1, +2
        'ep': (0, 9, 2, 3, 4, 8, 6, 7, 5, 1, 10, 11), # Cạnh: UF->FL, FL->DF, DF->FR, FR->UF
        'eo': (0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0), # Orientation changes for the 4 edges
    },
    # === Phép xoay mặt D (Down - dưới) 90 độ CW ===
    'D': {
        'cp': (0, 1, 2, 3, 5, 6, 7, 4), # Góc: DRF->DLF, DLF->DLB, DLB->DRB, DRB->DRF
        'co': (0, 0, 0, 0, 0, 0, 0, 0),
        'ep': (0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11), # Cạnh: DR->DF, DF->DL, DL->DB, DB->DR
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    },
    # === Phép xoay mặt L (Left - trái) 90 độ CW ===
    'L': {
        'cp': (0, 2, 6, 3, 4, 1, 5, 7), # Góc: ULF->ULB, ULB->DLB, DLB->DLF, DLF->ULF
        'co': (0, 1, 2, 0, 0, 2, 1, 0), # Orientation changes: +1, +2, +1, +2
        'ep': (0, 1, 10, 3, 4, 5, 9, 7, 8, 2, 6, 11), # Cạnh: UL->BL, BL->DL, DL->FL, FL->UL
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    },
    # === Phép xoay mặt B (Back - sau) 90 độ CW ===
    'B': {
        'cp': (0, 1, 3, 7, 4, 5, 2, 6), # Góc: ULB->URB, URB->DRB, DRB->DLB, DLB->ULB
        'co': (0, 0, 1, 2, 0, 0, 2, 1), # Orientation changes: +1, +2, +1, +2
        'ep': (0, 1, 2, 11, 4, 5, 6, 10, 8, 9, 7, 3), # Cạnh: UB->BR, BR->DB, DB->BL, BL->UB
        'eo': (0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1), # Orientation changes for the 4 edges
    },
    # === Phép xoay ngược chiều (CCW - prime) ===
    "U'": {
        'cp': (1, 2, 3, 0, 4, 5, 6, 7), # Inverse of U cp
        'co': (0, 0, 0, 0, 0, 0, 0, 0), # Inverse of U co
        'ep': (1, 2, 3, 0, 4, 5, 6, 7, 8, 9, 10, 11), # Inverse of U ep
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), # Inverse of U eo
    },
    "R'": {
        'cp': (3, 1, 2, 7, 0, 5, 6, 4), # Inverse of R cp
        'co': (1, 0, 0, 2, 2, 0, 0, 1), # Correct inverse orientation for R
        'ep': (8, 1, 2, 3, 11, 5, 6, 7, 0, 9, 10, 4), # Inverse of R ep
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), # Inverse of R eo
    },
    "F'": {
        'cp': (4, 0, 2, 3, 5, 1, 6, 7), # Inverse of F cp
        'co': (2, 1, 0, 0, 1, 2, 0, 0), # Correct inverse orientation for F
        'ep': (0, 9, 2, 3, 4, 8, 6, 7, 5, 1, 10, 11), # Inverse of F ep
        'eo': (0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0), # eo is same for F and F'
    },
    "D'": {
        'cp': (0, 1, 2, 3, 7, 4, 5, 6), # Inverse of D cp
        'co': (0, 0, 0, 0, 0, 0, 0, 0), # Inverse of D co
        'ep': (0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11), # Inverse of D ep
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), # Inverse of D eo
    },
    "L'": {
        'cp': (0, 5, 1, 3, 4, 6, 2, 7), # Inverse of L cp
        'co': (0, 2, 1, 0, 0, 1, 2, 0), # Correct inverse orientation for L
        'ep': (0, 1, 9, 3, 4, 5, 10, 7, 8, 6, 2, 11), # Inverse of L ep
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), # Inverse of L eo
    },
    "B'": {
        'cp': (0, 1, 6, 2, 4, 5, 7, 3), # Inverse of B cp
        'co': (0, 0, 2, 1, 0, 0, 1, 2), # Correct inverse orientation for B
        'ep': (0, 1, 2, 10, 4, 5, 6, 11, 8, 9, 7, 3), # Inverse of B ep
        'eo': (0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1), # eo is same for B and B'
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