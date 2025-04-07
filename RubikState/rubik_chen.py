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
    def __init__(self, cp=None, co=None, ep=None, eo=None):
        # Sử dụng tuple thay vì list để có hiệu suất tốt hơn
        if cp is None:
            cp = tuple(range(8))
        if co is None:
            co = tuple([0] * 8)
        if ep is None:
            ep = tuple(range(12))
        if eo is None:
            eo = tuple([0] * 12)
        
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
        
        # === Áp dụng hoán vị và định hướng GÓC ===
        new_cp = [0] * 8
        new_co = [0] * 8
        for i in range(8):
            new_cp[i] = self.cp[move_def['cp'][i]]
            new_co[i] = (self.co[move_def['cp'][i]] + move_def['co'][i]) % 3
        
        # === Áp dụng hoán vị và định hướng CẠNH ===
        new_ep = [0] * 12
        new_eo = [0] * 12
        for i in range(12):
            new_ep[i] = self.ep[move_def['ep'][i]]
            new_eo[i] = (self.eo[move_def['ep'][i]] + move_def['eo'][i]) % 2
        
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
    # === Phép xoay mặt L (Left - trái) 90 độ CW ===
    'L': {
        'cp': (0, 2, 6, 3, 4, 1, 5, 7),
        'co': (0, 2, 1, 0, 0, 1, 2, 0),
        'ep': (0, 1, 10, 3, 4, 5, 9, 7, 8, 2, 6, 11),
        'eo': (0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0)
    },
    # === Phép xoay mặt R (Right - phải) 90 độ CW ===
    'R': {
        'cp': (4, 1, 2, 0, 7, 5, 6, 3),
        'co': (1, 0, 0, 2, 2, 0, 0, 1),
        'ep': (8, 1, 2, 3, 11, 5, 6, 7, 4, 9, 10, 0),
        'eo': (1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1)
    },
    # === Phép xoay mặt F (Front - trước) 90 độ CW ===
    'F': {
        'cp': (1, 5, 2, 3, 0, 4, 6, 7),
        'co': (2, 1, 0, 0, 1, 2, 0, 0),
        'ep': (0, 9, 2, 3, 4, 8, 6, 7, 1, 5, 10, 11),
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },
    # === Phép xoay mặt U (Up - trên) 90 độ CW ===
    'U': {
        'cp': (3, 0, 1, 2, 4, 5, 6, 7),
        'co': (0, 0, 0, 0, 0, 0, 0, 0),
        'ep': (3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11),
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },
    # === Phép xoay mặt D (Down - dưới) 90 độ CW ===
    'D': {
        'cp': (0, 1, 2, 3, 5, 6, 7, 4),
        'co': (0, 0, 0, 0, 0, 0, 0, 0),
        'ep': (0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11),
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },
    # === Phép xoay mặt B (Back - sau) 90 độ CW ===
    'B': {
        'cp': (0, 1, 3, 7, 4, 5, 2, 6),
        'co': (0, 0, 2, 1, 0, 0, 1, 2),
        'ep': (0, 1, 2, 11, 4, 5, 6, 10, 8, 9, 3, 7),
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },
    # === Phép xoay ngược chiều (CCW - prime) ===
    "L'": {
        'cp': (0, 5, 1, 3, 4, 6, 2, 7),
        'co': (0, 2, 1, 0, 0, 1, 2, 0),
        'ep': (0, 1, 9, 3, 4, 5, 10, 7, 8, 6, 2, 11),
        'eo': (0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0)
    },
    "R'": {
        'cp': (3, 1, 2, 7, 0, 5, 6, 4),
        'co': (1, 0, 0, 2, 2, 0, 0, 1),
        'ep': (11, 1, 2, 3, 8, 5, 6, 7, 0, 9, 10, 4),
        'eo': (1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1)
    },
    "F'": {
        'cp': (4, 0, 2, 3, 5, 1, 6, 7),
        'co': (2, 1, 0, 0, 1, 2, 0, 0),
        'ep': (0, 8, 2, 3, 4, 9, 6, 7, 5, 1, 10, 11),
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },
    "B'": {
        'cp': (0, 1, 6, 2, 4, 5, 7, 3),
        'co': (0, 0, 2, 1, 0, 0, 1, 2),
        'ep': (0, 1, 2, 10, 4, 5, 6, 11, 8, 9, 7, 3),
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },
    "U'": {
        'cp': (1, 2, 3, 0, 4, 5, 6, 7),
        'co': (0, 0, 0, 0, 0, 0, 0, 0),
        'ep': (1, 2, 3, 0, 4, 5, 6, 7, 8, 9, 10, 11),
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    },
    "D'": {
        'cp': (0, 1, 2, 3, 7, 4, 5, 6),
        'co': (0, 0, 0, 0, 0, 0, 0, 0),
        'ep': (0, 1, 2, 3, 7, 4, 5, 6, 8, 9, 10, 11),
        'eo': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
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

def calculate_prime_moves():
    """
    Tính toán định nghĩa cho các phép xoay ngược (prime moves) bằng cách áp dụng phép xoay thuận 3 lần.
    """
    base_moves = ['U', 'R', 'F', 'D', 'L', 'B']
    prime_moves = {}
    
    for move in base_moves:
        # Khởi tạo trạng thái ban đầu
        initial_state = SOLVED_STATE_3x3
        
        # Áp dụng phép xoay 3 lần
        current_state = initial_state
        for _ in range(3):
            current_state = current_state.apply_move(move)
        
        # Trích xuất định nghĩa phép xoay ngược
        prime_move_def = {
            'cp': current_state.cp,
            'co': current_state.co,
            'ep': current_state.ep,
            'eo': current_state.eo
        }
        
        # Lưu vào từ điển
        prime_moves[f"{move}'"] = prime_move_def
    
    return prime_moves

def test_3x3():
    """
    Hàm kiểm tra toàn diện các định nghĩa phép xoay của Rubik 3x3.
    """
    def print_test_result(test_name, passed):
        print(f"{test_name}: {'✓ PASSED' if passed else '✗ FAILED'}")
    
    def states_equal(state1, state2):
        return (state1.cp == state2.cp and state1.co == state2.co and 
                state1.ep == state2.ep and state1.eo == state2.eo)
    
    def check_orientation_sum(state):
        # Kiểm tra tổng định hướng góc (phải chia hết cho 3)
        corner_sum = sum(state.co) % 3
        # Kiểm tra tổng định hướng cạnh (phải chia hết cho 2)
        edge_sum = sum(state.eo) % 2
        return corner_sum == 0 and edge_sum == 0
    
    def count_affected_pieces(state):
        """Đếm số lượng góc và cạnh bị ảnh hưởng so với trạng thái ban đầu"""
        corners = sum(1 for i in range(8) if state.cp[i] != i or state.co[i] != 0)
        edges = sum(1 for i in range(12) if state.ep[i] != i or state.eo[i] != 0)
        return corners, edges
    
    # Khởi tạo trạng thái ban đầu
    initial_state = SOLVED_STATE_3x3
    base_moves = ['U', 'R', 'F', 'D', 'L', 'B']
    all_tests_passed = True
    
    print("\n=== KIỂM TRA ĐỊNH NGHĨA PHÉP XOAY RUBIK 3x3 ===\n")
    
    # Test 1: Kiểm tra X' = X³
    print("1. Kiểm tra tính chất X' = X³:")
    for move in base_moves:
        # Áp dụng phép xoay 3 lần
        state_3x = initial_state
        for _ in range(3):
            state_3x = state_3x.apply_move(move)
        
        # Áp dụng phép xoay ngược
        state_prime = initial_state.apply_move(f"{move}'")
        
        # So sánh kết quả
        test_passed = states_equal(state_3x, state_prime)
        print_test_result(f"  {move}' = {move}³", test_passed)
        all_tests_passed &= test_passed
    
    # Test 2: Kiểm tra X⁴ = I
    print("\n2. Kiểm tra tính chất X⁴ = I:")
    for move in base_moves:
        state = initial_state
        for _ in range(4):
            state = state.apply_move(move)
        test_passed = states_equal(state, initial_state)
        print_test_result(f"  {move}⁴ = I", test_passed)
        all_tests_passed &= test_passed
    
    # Test 3: Kiểm tra XX' = X'X = I
    print("\n3. Kiểm tra tính chất XX' = X'X = I:")
    for move in base_moves:
        # Kiểm tra XX'
        state1 = initial_state.apply_move(move)
        state1 = state1.apply_move(f"{move}'")
        test_passed1 = states_equal(state1, initial_state)
        print_test_result(f"  {move}{move}' = I", test_passed1)
        
        # Kiểm tra X'X
        state2 = initial_state.apply_move(f"{move}'")
        state2 = state2.apply_move(move)
        test_passed2 = states_equal(state2, initial_state)
        print_test_result(f"  {move}'{move} = I", test_passed2)
        
        all_tests_passed &= test_passed1 and test_passed2
    
    # Test 4: Kiểm tra tính chất bảo toàn parity
    print("\n4. Kiểm tra tính chất bảo toàn parity:")
    for move in base_moves:
        state = initial_state.apply_move(move)
        corner_parity = calculate_parity(state.cp)
        edge_parity = calculate_parity(state.ep)
        test_passed = corner_parity == edge_parity
        print_test_result(f"  Parity sau phép xoay {move}", test_passed)
        all_tests_passed &= test_passed
    
    # Test 5: Kiểm tra tính chất bảo toàn định hướng tổng
    print("\n5. Kiểm tra tính chất bảo toàn định hướng tổng:")
    for move in base_moves:
        state = initial_state.apply_move(move)
        test_passed = check_orientation_sum(state)
        print_test_result(f"  Định hướng tổng sau phép xoay {move}", test_passed)
        all_tests_passed &= test_passed

    # Test 6: Kiểm tra tính chất giao hoán của các phép xoay mặt đối diện
    print("\n6. Kiểm tra tính chất giao hoán của các phép xoay mặt đối diện:")
    opposite_pairs = [('U', 'D'), ('L', 'R'), ('F', 'B')]
    for move1, move2 in opposite_pairs:
        state1 = initial_state.apply_move(move1).apply_move(move2)
        state2 = initial_state.apply_move(move2).apply_move(move1)
        test_passed = states_equal(state1, state2)
        print_test_result(f"  {move1}{move2} = {move2}{move1}", test_passed)
        all_tests_passed &= test_passed

    # Test 7: Kiểm tra tính chất KHÔNG giao hoán của các phép xoay mặt kề
    print("\n7. Kiểm tra tính chất không giao hoán của các phép xoay mặt kề:")
    adjacent_pairs = [('U', 'F'), ('U', 'R'), ('U', 'L'), ('U', 'B'),
                     ('D', 'F'), ('D', 'R'), ('D', 'L'), ('D', 'B'),
                     ('F', 'R'), ('F', 'L'), ('B', 'R'), ('B', 'L')]
    for move1, move2 in adjacent_pairs:
        state1 = initial_state.apply_move(move1).apply_move(move2)
        state2 = initial_state.apply_move(move2).apply_move(move1)
        test_passed = not states_equal(state1, state2)
        print_test_result(f"  {move1}{move2} ≠ {move2}{move1}", test_passed)
        all_tests_passed &= test_passed

    # Test 8: Kiểm tra tính chất (X²)² = I
    print("\n8. Kiểm tra tính chất (X²)² = I:")
    for move in base_moves:
        state = initial_state
        # Áp dụng X² hai lần
        for _ in range(2):
            for _ in range(2):
                state = state.apply_move(move)
        test_passed = states_equal(state, initial_state)
        print_test_result(f"  ({move}²)² = I", test_passed)
        all_tests_passed &= test_passed

    # Test 9: Kiểm tra số lượng góc và cạnh bị ảnh hưởng
    print("\n9. Kiểm tra số lượng góc và cạnh bị ảnh hưởng:")
    expected_affected = {
        'U': (4, 4), 'D': (4, 4),  # 4 góc, 4 cạnh
        'R': (4, 4), 'L': (4, 4),  # 4 góc, 4 cạnh
        'F': (4, 4), 'B': (4, 4)   # 4 góc, 4 cạnh
    }
    for move in base_moves:
        state = initial_state.apply_move(move)
        corners, edges = count_affected_pieces(state)
        exp_corners, exp_edges = expected_affected[move]
        test_passed = corners == exp_corners and edges == exp_edges
        print_test_result(f"  {move} ảnh hưởng {corners} góc, {edges} cạnh", test_passed)
        all_tests_passed &= test_passed

    # Test 10: Kiểm tra một số chuỗi phép xoay cơ bản
    print("\n10. Kiểm tra một số chuỗi phép xoay cơ bản:")
    algorithms = {
        "Sexy move": ["R", "U", "R'", "U'"],
        "Sune": ["R", "U", "R'", "U", "R", "U", "U", "R'"],
        "Double Sune": ["R", "U", "R'", "U", "R", "U", "U", "R'"],
        "Sledgehammer": ["R'", "F", "R", "F'"]
    }
    for name, moves in algorithms.items():
        state = initial_state
        for move in moves * 6:  # Lặp lại 6 lần
            state = state.apply_move(move)
        test_passed = states_equal(state, initial_state)
        print_test_result(f"  {name} × 6 = I", test_passed)
        all_tests_passed &= test_passed
    
    # Kết luận
    print(f"\nKết luận: {'✓ Tất cả test đều PASSED' if all_tests_passed else '✗ Có test bị FAILED'}")
    return all_tests_passed

if __name__ == "__main__":
    test_3x3()

# Tính toán các phép xoay ngược dựa trên phép xoay thuận
prime_moves = calculate_prime_moves()
# Thêm các phép xoay ngược vào từ điển MOVES_3x3
MOVES_3x3.update(prime_moves)

