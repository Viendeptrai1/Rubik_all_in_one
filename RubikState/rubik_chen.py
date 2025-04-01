"""
RubikState.py - Cài đặt lớp đối tượng mô phỏng khối Rubik 3x3
Sử dụng mã hóa các góc và cạnh theo chuẩn Kociemba để biểu diễn trạng thái.

Góc (Corners):
0: URF (Up-Right-Front)   1: ULF (Up-Left-Front)
2: ULB (Up-Left-Back)     3: URB (Up-Right-Back)
4: DRF (Down-Right-Front) 5: DLF (Down-Left-Front)
6: DLB (Down-Left-Back)   7: DRB (Down-Right-Back)

Cạnh (Edges):
0: UR (Up-Right)     1: UF (Up-Front)      2: UL (Up-Left)      3: UB (Up-Back)
4: DR (Down-Right)   5: DF (Down-Front)    6: DL (Down-Left)    7: DB (Down-Back)
8: FR (Front-Right)  9: FL (Front-Left)    10: BL (Back-Left)   11: BR (Back-Right)

Định hướng:
- Góc: 0 = đúng hướng, 1 = xoay 120° theo chiều kim đồng hồ, 2 = xoay 240° theo chiều kim đồng hồ
- Cạnh: 0 = đúng hướng, 1 = bị lật
"""

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
# ĐỊNH NGHĨA CHUẨN MOVES_3x3 - PHIÊN BẢN KOCIEMBA VERIFIED
MOVES_3x3 = {
    # === Phép xoay mặt U (Up - trên) 90 độ CW ===
    'U': {
        'cp': (3, 0, 1, 2, 4, 5, 6, 7), # Góc: giống với 2x2
        'co': (0, 0, 0, 0, 0, 0, 0, 0), # Hướng góc không đổi
        'ep': (3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11), # Cạnh: UB->UR->UF->UL->UB
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) # Hướng cạnh không đổi
    },
    # === Phép xoay mặt R (Right - phải) 90 độ CW ===
    'R': {
        'cp': (4, 1, 2, 0, 7, 5, 6, 3), # Góc: giống với 2x2
        'co': (2, 0, 0, 1, 1, 0, 0, 2), # Hướng: giống với 2x2
        'ep': (8, 1, 2, 3, 11, 5, 6, 7, 4, 9, 10, 0), # Cạnh: UR(0)->FR(8)->DR(4)->BR(11)->UR
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) # Hướng cạnh không đổi khi xoay R
    },
    # === Phép xoay mặt F (Front - trước) 90 độ CW ===
    'F': {
        'cp': (1, 5, 2, 3, 0, 4, 6, 7), # Góc: giống với 2x2
        'co': (1, 2, 0, 0, 2, 1, 0, 0), # Hướng: giống với 2x2
        'ep': (0, 8, 2, 3, 4, 9, 6, 7, 5, 1, 10, 11), # Cạnh: UF->RF->DF->LF->UF
        'eo': (0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0) # UF, RF, DF, LF bị đảo hướng
    },
    # === Phép xoay mặt D (Down - dưới) 90 độ CW ===
    'D': {
        'cp': (0, 1, 2, 3, 5, 6, 7, 4), # Góc: giống với 2x2
        'co': (0, 0, 0, 0, 0, 0, 0, 0), # Hướng góc không đổi
        'ep': (0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11), # Cạnh: DF->DL->DB->DR->DF
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) # Hướng cạnh không đổi
    },
    # === Phép xoay mặt L (Left - trái) 90 độ CW ===
    'L': {
        'cp': (0, 2, 6, 3, 4, 1, 5, 7), # Góc: giống với 2x2
        'co': (0, 1, 2, 0, 0, 2, 1, 0), # Hướng: giống với 2x2
        'ep': (0, 1, 9, 3, 4, 5, 10, 7, 8, 6, 2, 11), 
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },
    # === Phép xoay mặt B (Back - sau) 90 độ CW ===
    'B': {
        'cp': (0, 1, 3, 7, 4, 5, 2, 6), # Góc: giống với 2x2
        'co': (0, 0, 1, 2, 0, 0, 2, 1), # Hướng: giống với 2x2
        'ep': (3, 1, 2, 7, 4, 5, 6, 10, 8, 9, 0, 11), # Cạnh: UB->LB->DB->RB (cyclic)
        'eo': (1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0) # UB, LB, DB, RB bị đảo hướng
    },
    # === Phép xoay ngược chiều (CCW - prime) - giữ nguyên từ 2x2 ===
    "U'": {
        'cp': (1, 2, 3, 0, 4, 5, 6, 7), # Nghịch đảo cp của U
        'co': (0, 0, 0, 0, 0, 0, 0, 0), # Hướng không đổi
        'ep': (1, 2, 3, 0, 4, 5, 6, 7, 8, 9, 10, 11), # Cạnh: UL->UF->UR->UB->UL
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) # Hướng không đổi
    },
    "R'": {
        'cp': (3, 1, 2, 7, 0, 5, 6, 4), # Nghịch đảo cp của R
        'co': (2, 0, 0, 1, 1, 0, 0, 2), # Hướng ngược (giống 2x2)
        'ep': (11, 1, 2, 3, 8, 5, 6, 7, 0, 9, 10, 4), # Cạnh: UR(0)->BR(11)->DR(4)->FR(8)->UR
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) # Hướng cạnh không đổi khi xoay R'
    },
    "F'": {
        'cp': (4, 0, 2, 3, 5, 1, 6, 7), # Nghịch đảo cp của F
        'co': (1, 2, 0, 0, 2, 1, 0, 0), # Hướng ngược (giống 2x2)
        'ep': (0, 9, 2, 3, 4, 8, 6, 7, 1, 5, 10, 11), # Cạnh: LF->DF->RF->UF->LF
        'eo': (0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0) # UF, RF, DF, LF đảo hướng
    },
    "D'": {
        'cp': (0, 1, 2, 3, 7, 4, 5, 6), # Nghịch đảo cp của D
        'co': (0, 0, 0, 0, 0, 0, 0, 0), # Hướng không đổi
        'ep': (0, 1, 2, 3, 7, 4, 5, 6, 8, 9, 10, 11), # Cạnh: DR->DB->DL->DF->DR
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) # Hướng không đổi
    },
    "L'": {
        'cp': (0, 5, 1, 3, 4, 6, 2, 7), # Nghịch đảo cp của L
        'co': (0, 1, 2, 0, 0, 2, 1, 0), # Hướng ngược (giống 2x2)
        'ep': (0, 1, 10, 3, 4, 5, 9, 7, 8, 2, 6, 11), 
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },
    "B'": {
        'cp': (0, 1, 6, 2, 4, 5, 7, 3), # Nghịch đảo cp của B
        'co': (0, 0, 1, 2, 0, 0, 2, 1), # Hướng ngược (giống 2x2)
        'ep': (10, 1, 2, 0, 4, 5, 6, 3, 8, 9, 7, 11), # Nghịch đảo ep của B: RB->DB->LB->UB
        'eo': (1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0) # UB, LB, DB, RB đảo hướng
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