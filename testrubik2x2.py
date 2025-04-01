from RubikState.rubik_2x2 import Rubik2x2State, SOLVED_STATE_2x2, MOVES_2x2, heuristic_2x2
from RubikState.rubik_solver import bfs, a_star, ida_star
import time
import random
import copy

def test_move_consistency():
    """Kiểm tra tính nhất quán của các phép xoay"""
    print("\n=== KIỂM TRA TÍNH NHẤT QUÁN CỦA CÁC PHÉP XOAY ===")
    
    state = SOLVED_STATE_2x2.copy()
    
    # Kiểm tra từng phép xoay và phép ngược của nó
    for move in MOVES_2x2.keys():
        if move.endswith("'"):  # Bỏ qua các phép ngược vì sẽ kiểm tra chúng theo cặp
            continue
            
        move_prime = move + "'"
        
        # Áp dụng phép xoay và phép ngược của nó
        test_state = state.copy()
        test_state = test_state.apply_move(move, MOVES_2x2)
        test_state = test_state.apply_move(move_prime, MOVES_2x2)
        
        if test_state == state:
            print(f"✓ {move} và {move_prime} hoạt động đúng (trở về trạng thái ban đầu)")
        else:
            print(f"✗ LỖI: {move} và {move_prime} KHÔNG trở về trạng thái ban đầu!")
            print(f"  Ban đầu: CP={state.cp}, CO={state.co}")
            print(f"  Sau khi áp dụng: CP={test_state.cp}, CO={test_state.co}")
            
    # Kiểm tra phép xoay hai lần
    double_moves = {
        "R R": ["R", "R"],
        "U U": ["U", "U"],
        "F F": ["F", "F"],
        "L L": ["L", "L"],
        "D D": ["D", "D"],
        "B B": ["B", "B"]
    }
    
    for name, moves in double_moves.items():
        # Áp dụng phép xoay hai lần sẽ trở về ban đầu sau 2 lần
        test_state = state.copy()
        for _ in range(2):
            for move in moves:
                test_state = test_state.apply_move(move, MOVES_2x2)
                
        if test_state == state:
            print(f"✓ {name} x2 hoạt động đúng (trở về ban đầu sau 2 lần)")
        else:
            print(f"✗ LỖI: {name} x2 KHÔNG trở về trạng thái ban đầu sau 2 lần!")
    
    # Kiểm tra phép xoay 4 lần
    for move in ["R", "U", "F", "L", "D", "B"]:
        # Áp dụng phép xoay 4 lần sẽ trở về ban đầu
        test_state = state.copy()
        for _ in range(4):
            test_state = test_state.apply_move(move, MOVES_2x2)
            
        if test_state == state:
            print(f"✓ {move} x4 hoạt động đúng (trở về ban đầu sau 4 lần)")
        else:
            print(f"✗ LỖI: {move} x4 KHÔNG trở về trạng thái ban đầu sau 4 lần!")

def test_algorithms():
    """Kiểm tra các thuật toán nổi tiếng có hoạt động đúng không"""
    print("\n=== KIỂM TRA CÁC THUẬT TOÁN NỔI TIẾNG ===")
    
    state = SOLVED_STATE_2x2.copy()
    
    # Kiểm tra sexy move (R U R' U') x6 = trạng thái ban đầu
    sexy_move = ["R", "U", "R'", "U'"]
    test_state = state.copy()
    
    print("Sexy move (R U R' U') x6:")
    for i in range(6):
        for move in sexy_move:
            test_state = test_state.apply_move(move, MOVES_2x2)
        print(f"  Lần {i+1}: {'Khớp' if test_state == state else 'Không khớp'} với trạng thái ban đầu")
    
    if test_state == state:
        print("✓ Sexy move x6 hoạt động đúng!")
    else:
        print("✗ LỖI: Sexy move x6 KHÔNG trở về trạng thái ban đầu!")
        
    # Kiểm tra Sune (R U R' U R U U R')
    sune = ["R", "U", "R'", "U", "R", "U", "U", "R'"]
    test_state = state.copy()
    
    print("\nSune (R U R' U R U U R'):")
    # Áp dụng Sune với các số lần khác nhau và in trạng thái
    for i in range(1, 7):  # Sune x6 thường trở về ban đầu
        temp_state = test_state.copy()
        for _ in range(i):
            for move in sune:
                temp_state = temp_state.apply_move(move, MOVES_2x2)
        print(f"  Sune x{i}: {'Khớp' if temp_state == state else 'Không khớp'} với trạng thái ban đầu")
    
    # Kiểm tra thuật toán Y-perm (một thuật toán PLL phổ biến cho 2x2)
    y_perm = ["F", "R", "U'", "R'", "U'", "R", "U", "R'", "F'", "R", "U", "R'", "U'", "R'", "F", "R", "F'"]
    test_state = state.copy()
    
    print("\nY-Perm:")
    for move in y_perm:
        test_state = test_state.apply_move(move, MOVES_2x2)
        
    y_perm_changes = test_state != state
    print(f"  Y-Perm thay đổi trạng thái: {'Có' if y_perm_changes else 'Không'} (nên là Có)")
    
    # Áp dụng Y-Perm một lần nữa để kiểm tra
    for move in y_perm:
        test_state = test_state.apply_move(move, MOVES_2x2)
    
    y_perm_double = test_state == state
    print(f"  Y-Perm x2: {'Khớp' if y_perm_double else 'Không khớp'} với trạng thái ban đầu")
    
def test_bidirectional_moves():
    """Kiểm tra việc áp dụng đường đi xuôi và ngược"""
    print("\n=== KIỂM TRA ÁP DỤNG ĐƯỜNG ĐI XUÔI VÀ NGƯỢC ===")
    
    # Tạo một chuỗi nước đi ngẫu nhiên
    moves = ["R", "U", "F", "L", "D", "B", "R'", "U'", "F'", "L'", "D'", "B'"]
    scramble = random.choices(moves, k=8)
    
    print(f"Chuỗi xáo trộn: {' '.join(scramble)}")
    
    # Áp dụng chuỗi xáo trộn
    state = SOLVED_STATE_2x2.copy()
    scrambled_state = state.copy()
    
    print("\nÁp dụng từng nước đi:")
    for i, move in enumerate(scramble):
        scrambled_state = scrambled_state.apply_move(move, MOVES_2x2)
        print(f"  Bước {i+1}: {move}")
    
    # Tạo đường đi ngược (đảo ngược thứ tự và đổi nước đi thành nước đi ngược)
    reverse_path = []
    for move in reversed(scramble):
        if "'" in move:
            reverse_path.append(move.replace("'", ""))
        else:
            reverse_path.append(move + "'")
    
    print(f"\nĐường đi ngược: {' '.join(reverse_path)}")
    
    # Áp dụng đường đi ngược
    recovered_state = scrambled_state.copy()
    
    print("\nÁp dụng từng nước đi ngược:")
    for i, move in enumerate(reverse_path):
        recovered_state = recovered_state.apply_move(move, MOVES_2x2)
        print(f"  Bước {i+1}: {move}")
    
    # So sánh kết quả
    if recovered_state == state:
        print("✓ Áp dụng đường đi ngược hoạt động đúng (trở về trạng thái ban đầu)!")
    else:
        print("✗ LỖI: Áp dụng đường đi ngược KHÔNG trở về trạng thái ban đầu!")
        print(f"  Trạng thái ban đầu: CP={state.cp}, CO={state.co}")
        print(f"  Trạng thái sau khi áp dụng đường đi ngược: CP={recovered_state.cp}, CO={recovered_state.co}")

def test_heuristic():
    """Kiểm tra hàm heuristic"""
    print("\n=== KIỂM TRA HÀM HEURISTIC ===")
    
    state = SOLVED_STATE_2x2.copy()
    
    # Kiểm tra heuristic của trạng thái đã giải
    h = heuristic_2x2(state)
    print(f"Heuristic của trạng thái đã giải: {h} (nên bằng 0)")
    
    # Áp dụng các nước đi và kiểm tra heuristic
    test_moves = [
        [],  # Không có nước đi
        ["R"],  # 1 nước đi
        ["R", "U"],  # 2 nước đi
        ["R", "U", "R'"],  # 3 nước đi
        ["R", "U", "R'", "U'"],  # 4 nước đi
        ["R", "U", "R'", "U'", "R"],  # 5 nước đi
    ]
    
    for moves in test_moves:
        test_state = state.copy()
        for move in moves:
            test_state = test_state.apply_move(move, MOVES_2x2)
        
        h = heuristic_2x2(test_state)
        print(f"Heuristic sau {len(moves)} nước đi ({' '.join(moves) if moves else 'không có'}): {h}")

def test_search_algorithms(max_depth=5):
    """Kiểm tra các thuật toán tìm kiếm với độ sâu tăng dần"""
    print(f"\n=== KIỂM TRA CÁC THUẬT TOÁN TÌM KIẾM (tối đa {max_depth} nước) ===")
    
    state = SOLVED_STATE_2x2.copy()
    
    for depth in range(1, max_depth + 1):
        print(f"\n--- Độ sâu {depth} ---")
        
        # Tạo một chuỗi xáo trộn ngẫu nhiên với độ sâu đã chọn
        moves = ["R", "U", "F", "L", "D", "B", "R'", "U'", "F'", "L'", "D'", "B'"]
        scramble = random.choices(moves, k=depth)
        
        print(f"Chuỗi xáo trộn: {' '.join(scramble)}")
        
        # Áp dụng chuỗi xáo trộn
        scrambled_state = state.copy()
        for move in scramble:
            scrambled_state = scrambled_state.apply_move(move, MOVES_2x2)
        
        # Lưu trữ chuỗi xáo trộn ngược để so sánh
        reverse_scramble = []
        for move in reversed(scramble):
            if "'" in move:
                reverse_scramble.append(move.replace("'", ""))
            else:
                reverse_scramble.append(move + "'")
        
        
        # Kiểm tra thuật toán A*
        print("\nKiểm tra A*:")
        astar_state = Rubik2x2State(scrambled_state.cp, scrambled_state.co)
        start_time = time.time()
        astar_path, astar_nodes, astar_time = a_star(astar_state, time_limit=60)
        print(f"  Thời gian: {astar_time:.4f}s, Số nút đã duyệt: {astar_nodes}")
        
        if astar_path:
            print(f"  Độ dài lời giải: {len(astar_path)}")
            print(f"  Lời giải: {' '.join(astar_path)}")
            
            # Kiểm tra xem lời giải có đúng không
            test_state = astar_state.copy()
            for move in astar_path:
                test_state = test_state.apply_move(move, MOVES_2x2)
            
            if test_state == state:
                print("  ✓ Lời giải A* hoạt động đúng!")
            else:
                print("  ✗ LỖI: Lời giải A* KHÔNG đưa về trạng thái đã giải!")
                
                # Thử đảo ngược lời giải
                print("  Thử nghiệm đảo ngược lời giải A*:")
                test_state = astar_state.copy()
                for move in reversed(astar_path):
                    if "'" in move:
                        inverse_move = move.replace("'", "")
                    else:
                        inverse_move = move + "'"
                    test_state = test_state.apply_move(inverse_move, MOVES_2x2)
                
                if test_state == state:
                    print("  ✓ Lời giải đảo ngược hoạt động đúng!")
                else:
                    print("  ✗ Lời giải đảo ngược cũng KHÔNG đúng!")
        else:
            print("  Không tìm thấy lời giải bằng A*!")
        
        # Kiểm tra thuật toán IDA*
        print("\nKiểm tra IDA*:")
        ida_state = Rubik2x2State(scrambled_state.cp, scrambled_state.co)
        start_time = time.time()
        ida_path, ida_nodes, ida_time = ida_star(ida_state, time_limit=60)
        print(f"  Thời gian: {ida_time:.4f}s, Số nút đã duyệt: {ida_nodes}")
        
        if ida_path:
            print(f"  Độ dài lời giải: {len(ida_path)}")
            print(f"  Lời giải: {' '.join(ida_path)}")
            
            # Kiểm tra xem lời giải có đúng không
            test_state = ida_state.copy()
            for move in ida_path:
                test_state = test_state.apply_move(move, MOVES_2x2)
            
            if test_state == state:
                print("  ✓ Lời giải IDA* hoạt động đúng!")
            else:
                print("  ✗ LỖI: Lời giải IDA* KHÔNG đưa về trạng thái đã giải!")
                
                # Thử đảo ngược lời giải
                print("  Thử nghiệm đảo ngược lời giải IDA*:")
                test_state = ida_state.copy()
                for move in reversed(ida_path):
                    if "'" in move:
                        inverse_move = move.replace("'", "")
                    else:
                        inverse_move = move + "'"
                    test_state = test_state.apply_move(inverse_move, MOVES_2x2)
                
                if test_state == state:
                    print("  ✓ Lời giải đảo ngược hoạt động đúng!")
                else:
                    print("  ✗ Lời giải đảo ngược cũng KHÔNG đúng!")
        else:
            print("  Không tìm thấy lời giải bằng IDA*!")

def test_class_methods():
    """Kiểm tra các phương thức của lớp Rubik2x2State"""
    print("\n=== KIỂM TRA CÁC PHƯƠNG THỨC CỦA LỚP RUBIK2X2STATE ===")
    
    # Tạo một trạng thái đã giải
    state = SOLVED_STATE_2x2.copy()
    
    # Kiểm tra phương thức copy
    state_copy = state.copy()
    print(f"Copy đúng? {'Đúng' if state == state_copy else 'Sai'}")
    
    # Kiểm tra phương thức __eq__
    print("\nKiểm tra __eq__:")
    state1 = Rubik2x2State(state.cp, state.co)
    state2 = Rubik2x2State(state.cp, state.co)
    print(f"  Hai trạng thái giống nhau: {state1 == state2}")
    
    # Thay đổi một chút
    state2 = Rubik2x2State(state.cp, state.co)
    state2 = state2.apply_move("R", MOVES_2x2)
    print(f"  Hai trạng thái khác nhau: {state1 != state2}")
    
    # Kiểm tra phương thức __hash__
    print("\nKiểm tra __hash__:")
    state_set = {state1, state2}
    print(f"  Số phần tử trong set: {len(state_set)} (nên là 2)")
    
    # Kiểm tra hash của trạng thái đã giải
    print(f"  Hash của trạng thái đã giải: {hash(state1)}")

def test_complex_scrambles():
    """Kiểm tra các công thức xáo trộn phức tạp"""
    print("\n=== KIỂM TRA CÁC CÔNG THỨC XÁO TRỘN PHỨC TẠP ===")
    
    state = SOLVED_STATE_2x2.copy()
    
    # Danh sách các chuỗi xáo trộn phức tạp
    complex_scrambles = [
        ["R", "U", "R'", "U'", "R'", "F", "R", "F'"],  # OLL đơn giản
        ["R", "U", "R'", "U", "R", "U", "U", "R'"],    # Sune
        ["R", "U'", "R", "F", "R'", "U", "R", "F'", "R", "R", "U'", "R'", "U'"], # PBL (Permutation of Both Layers)
    ]
    
    for i, scramble in enumerate(complex_scrambles):
        print(f"\nCông thức phức tạp {i+1}: {' '.join(scramble)}")
        
        # Áp dụng chuỗi xáo trộn
        scrambled_state = state.copy()
        for move in scramble:
            scrambled_state = scrambled_state.apply_move(move, MOVES_2x2)
        
        # So sánh với trạng thái đã giải
        if scrambled_state == state:
            print("  Cảnh báo: Công thức đã quay về trạng thái đã giải!")
            continue
        
        # Thử A* cho TẤT CẢ trường hợp
        print("\n  Thử A* cho công thức này:")
        astar_state = Rubik2x2State(scrambled_state.cp, scrambled_state.co)
        astar_path, astar_nodes, astar_time = a_star(astar_state, time_limit=60)
        
        if astar_path:
            print(f"  Tìm thấy lời giải trong {astar_time:.4f}s, {astar_nodes} nút đã duyệt")
            print(f"  Độ dài lời giải: {len(astar_path)}")
            print(f"  Lời giải: {' '.join(astar_path)}")
            
            # Kiểm tra tính đúng đắn của lời giải
            test_state = astar_state.copy()
            for move in astar_path:
                test_state = test_state.apply_move(move, MOVES_2x2)
            
            if test_state == state:
                print("  ✓ Lời giải A* hoạt động đúng!")
            else:
                print("  ✗ LỖI: Lời giải A* KHÔNG đưa về trạng thái đã giải!")
        else:
            print("  Không tìm thấy lời giải bằng A* trong thời gian cho phép!")

def test_move_definitions():
    """Kiểm tra định nghĩa phép xoay của Rubik 2x2"""
    print("\n=== KIỂM TRA ĐỊNH NGHĨA PHÉP XOAY CỦA RUBIK 2X2 ===")
    
    # Kiểm tra tính đối xứng của các phép xoay
    # Phép xoay và phép nghịch đảo của nó sẽ cho kết quả giống nhau trên trạng thái đối xứng
    
    state = SOLVED_STATE_2x2.copy()
    
    # Danh sách các phép xoay và phép nghịch đảo
    moves_pairs = [
        ("R", "R'"),
        ("U", "U'"),
        ("F", "F'"),
        ("L", "L'"),
        ("D", "D'"),
        ("B", "B'")
    ]
    
    for move, inverse in moves_pairs:
        print(f"\nKiểm tra tính đối xứng của {move} và {inverse}:")
        
        # Áp dụng phép xoay
        state1 = state.copy()
        state1 = state1.apply_move(move, MOVES_2x2)
        
        # Áp dụng phép nghịch đảo
        state2 = state.copy()
        state2 = state2.apply_move(inverse, MOVES_2x2)
        
        # Kiểm tra xem phép xoay và phép nghịch đảo có hoán đổi đúng các khối không
        # Góc 0 sau khi xoay R sẽ đi đến vị trí X
        # Góc X sau khi xoay R' sẽ đi đến vị trí 0
        
        move_cp = MOVES_2x2[move]['cp']
        inverse_cp = MOVES_2x2[inverse]['cp']
        
        consistency = True
        for i in range(8):
            # Nếu i->j trong phép xoay chính, thì j->i trong phép xoay nghịch đảo
            j = move_cp.index(i)
            if inverse_cp[i] != j:
                consistency = False
                print(f"  ✗ LỖI: Góc {i} di chuyển đến {move_cp[i]} trong {move}, nhưng từ {inverse_cp[i]} đến {i} trong {inverse}")
        
        if consistency:
            print(f"  ✓ Hoán vị góc trong {move} và {inverse} là nhất quán")
        else:
            print(f"  ✗ LỖI: Hoán vị góc trong {move} và {inverse} KHÔNG nhất quán!")
        
        # Kiểm tra định hướng
        move_co = MOVES_2x2[move]['co']
        inverse_co = MOVES_2x2[inverse]['co']
        
        orientation_consistency = True
        for i in range(8):
            # TODO: Kiểm tra định hướng phức tạp hơn
            pass
        
        # Kiểm tra tính đối xứng bằng cách áp dụng cả hai phép xoay
        test_state = state.copy()
        test_state = test_state.apply_move(move, MOVES_2x2)
        test_state = test_state.apply_move(inverse, MOVES_2x2)
        
        if test_state == state:
            print(f"  ✓ {move} rồi {inverse} trở về trạng thái ban đầu")
        else:
            print(f"  ✗ LỖI: {move} rồi {inverse} KHÔNG trở về trạng thái ban đầu!")

def test_specific_formula():
    """Kiểm tra một công thức cụ thể và xác minh lời giải của thuật toán"""
    print("\n=== KIỂM TRA CÔNG THỨC CỤ THỂ ===")
    
    # Trạng thái ban đầu
    state = SOLVED_STATE_2x2.copy()
    
    # Công thức cần kiểm tra
    formula = ["R", "U", "R'", "U'", "R'", "F", "R", "F'"]
    print(f"Công thức: {' '.join(formula)}")
    
    # Áp dụng công thức
    scrambled_state = state.copy()
    for move in formula:
        scrambled_state = scrambled_state.apply_move(move, MOVES_2x2)
    print("Đã áp dụng công thức")
    
    # In ra trạng thái sau khi áp dụng công thức
    print(f"Trạng thái sau khi áp dụng công thức:")
    print(f"  CP = {scrambled_state.cp}")
    print(f"  CO = {scrambled_state.co}")
    
    # Tạo công thức đảo ngược
    reverse_formula = []
    for move in reversed(formula):
        if "'" in move:
            reverse_formula.append(move.replace("'", ""))
        else:
            reverse_formula.append(move + "'")
    
    print(f"\nCông thức đảo ngược lý thuyết: {' '.join(reverse_formula)}")
    
    # Áp dụng công thức đảo ngược
    recovered_state = scrambled_state.copy()
    for move in reverse_formula:
        recovered_state = recovered_state.apply_move(move, MOVES_2x2)
    
    # Kiểm tra xem công thức đảo ngược có đưa về trạng thái ban đầu không
    if recovered_state == state:
        print("✓ Công thức đảo ngược hoạt động đúng (trở về trạng thái ban đầu)")
    else:
        print("✗ LỖI: Công thức đảo ngược KHÔNG đưa về trạng thái ban đầu!")
        print(f"  CP = {recovered_state.cp}")
        print(f"  CO = {recovered_state.co}")
    
    # Kiểm tra các thuật toán tìm kiếm
    print("\nKiểm tra BFS:")
    bfs_state = Rubik2x2State(scrambled_state.cp, scrambled_state.co)
    bfs_path, bfs_nodes, bfs_time = bfs(bfs_state, time_limit=60)
    
    if bfs_path:
        print(f"Lời giải BFS tìm được: {' '.join(bfs_path)}")
        print(f"Độ dài lời giải: {len(bfs_path)}")
        print(f"Số nút đã duyệt: {bfs_nodes}")
        print(f"Thời gian: {bfs_time:.4f}s")
        
        # So sánh với công thức đảo ngược
        matches_reverse = ' '.join(bfs_path) == ' '.join(reverse_formula)
        print(f"Lời giải BFS có khớp với công thức đảo ngược? {'Có' if matches_reverse else 'Không'}")
        
        # Áp dụng lời giải BFS
        test_state = bfs_state.copy()
        print("\nKiểm tra lời giải BFS từng bước:")
        for i, move in enumerate(bfs_path):
            test_state = test_state.apply_move(move, MOVES_2x2)
            print(f"  Bước {i+1}: {move} -> CP={test_state.cp}, CO={test_state.co}")
        
        if test_state == state:
            print("✓ Lời giải BFS đúng (trở về trạng thái ban đầu)")
        else:
            print("✗ LỖI: Lời giải BFS sai (không trở về trạng thái ban đầu)!")
            print(f"  CP = {test_state.cp}")
            print(f"  CO = {test_state.co}")
    else:
        print("Không tìm thấy lời giải bằng BFS!")
    
    print("\nKiểm tra A*:")
    astar_state = Rubik2x2State(scrambled_state.cp, scrambled_state.co)
    astar_path, astar_nodes, astar_time = a_star(astar_state, time_limit=60)
    
    if astar_path:
        print(f"Lời giải A* tìm được: {' '.join(astar_path)}")
        print(f"Độ dài lời giải: {len(astar_path)}")
        print(f"Số nút đã duyệt: {astar_nodes}")
        print(f"Thời gian: {astar_time:.4f}s")
        
        # So sánh với công thức đảo ngược
        matches_reverse = ' '.join(astar_path) == ' '.join(reverse_formula)
        print(f"Lời giải A* có khớp với công thức đảo ngược? {'Có' if matches_reverse else 'Không'}")
        
        # Áp dụng lời giải A*
        test_state = astar_state.copy()
        print("\nKiểm tra lời giải A* từng bước:")
        for i, move in enumerate(astar_path):
            test_state = test_state.apply_move(move, MOVES_2x2)
            print(f"  Bước {i+1}: {move} -> CP={test_state.cp}, CO={test_state.co}")
        
        if test_state == state:
            print("✓ Lời giải A* đúng (trở về trạng thái ban đầu)")
        else:
            print("✗ LỖI: Lời giải A* sai (không trở về trạng thái ban đầu)!")
            print(f"  CP = {test_state.cp}")
            print(f"  CO = {test_state.co}")
    else:
        print("Không tìm thấy lời giải bằng A*!")

def test_fixed_algorithms():
    """Kiểm tra danh sách các công thức cố định và lời giải tương ứng"""
    print("\n=== KIỂM TRA CÁC CÔNG THỨC CỐ ĐỊNH ===")
    
    # Trạng thái ban đầu
    state = SOLVED_STATE_2x2.copy()
    
    # Danh sách các công thức cần kiểm tra và lời giải dự kiến
    # Mỗi phần tử là (tên, công thức, lời giải chính xác, mô tả)
    test_cases = [
        (
            "OLL 1 (Anti-Sune)", 
            ["R", "U", "R'", "U'", "R'", "F", "R", "F'"], 
            ["F", "R'", "F'", "R", "U", "R", "U'", "R'"], 
            "Công thức OLL 1"
        ),
        (
            "Sexy move", 
            ["R", "U", "R'", "U'"], 
            ["U", "R", "U'", "R'"], 
            "Công thức cơ bản 'sexy move'"
        ),
        (
            "Sune", 
            ["R", "U", "R'", "U", "R", "U", "U", "R'"], 
            ["R", "U", "U", "R'", "U'", "R", "U'", "R'"], 
            "Công thức Sune (OLL 27)"
        ),
        # --- Thêm các trường hợp mới --- 
        (
            "T-Perm (PLL)",
            ["R", "U", "R'", "U'", "R'", "F", "R", "R", "U'", "R'", "U'", "R", "U", "R'", "F'"],
            ["F", "R", "U'", "R'", "U", "R", "U", "R'", "F'", "R", "U", "R'", "U'", "R'", "F", "R", "F'"],
            "Hoán vị 2 góc kề (T-Perm)"
        ),
        (
            "Y-Perm (PLL)",
            ["F", "R", "U'", "R'", "U'", "R", "U", "R'", "F'", "R", "U", "R'", "U'", "R'", "F", "R", "F'"],
            ["F", "R'", "F'", "R", "U", "R", "U'", "R'", "F", "R", "U", "R'", "U'", "R'", "U", "R", "U"], # Inverse Y-Perm
            "Hoán vị 2 góc chéo (Y-Perm)"
        ),
        (
            "OLL 26 (H-Perm like)",
            ["R", "U", "U", "R'", "U'", "R", "U'", "R'"], # Anti-Sune
            ["R", "U", "R'", "U", "R", "U", "U", "R'"], # Sune
            "Một trường hợp OLL khác"
        ),
        # ------------------------------
    ]
    
    for name, formula, expected_solution, description in test_cases:
        print(f"\n--- {name}: {description} ---")
        print(f"Công thức: {' '.join(formula)}")
        print(f"Lời giải dự kiến: {' '.join(expected_solution)}")
        
        # Áp dụng công thức
        scrambled_state = state.copy()
        for move in formula:
            scrambled_state = scrambled_state.apply_move(move, MOVES_2x2)
        
        # Tìm lời giải bằng BFS
        print("Tìm lời giải bằng BFS:")
        bfs_state = Rubik2x2State(scrambled_state.cp, scrambled_state.co)
        bfs_path, bfs_nodes, bfs_time = bfs(bfs_state, time_limit=60)
        
        if bfs_path:
            print(f"Lời giải tìm được: {' '.join(bfs_path)}")
            print(f"Số nút duyệt: {bfs_nodes}, Thời gian: {bfs_time:.4f}s")
            
            # So sánh với lời giải dự kiến
            is_expected = ' '.join(bfs_path) == ' '.join(expected_solution)
            print(f"Khớp với lời giải dự kiến? {'Có' if is_expected else 'Không'}")
            
            # Kiểm tra tính đúng đắn của lời giải
            test_state = bfs_state.copy()
            for move in bfs_path:
                test_state = test_state.apply_move(move, MOVES_2x2)
            
            if test_state == state:
                print(f"✓ Lời giải hoạt động đúng!")
            else:
                print(f"✗ LỖI: Lời giải KHÔNG hoạt động đúng!")
                print(f"  CP = {test_state.cp}, CO = {test_state.co}")
        else:
            print("Không tìm thấy lời giải bằng BFS!")
        
        # Tìm lời giải bằng A*
        print("\nTìm lời giải bằng A*:")
        astar_state = Rubik2x2State(scrambled_state.cp, scrambled_state.co)
        astar_path, astar_nodes, astar_time = a_star(astar_state, time_limit=60)
        
        if astar_path:
            print(f"Lời giải tìm được: {' '.join(astar_path)}")
            print(f"Số nút duyệt: {astar_nodes}, Thời gian: {astar_time:.4f}s")
            
            # So sánh với lời giải dự kiến
            is_expected = ' '.join(astar_path) == ' '.join(expected_solution)
            print(f"Khớp với lời giải dự kiến? {'Có' if is_expected else 'Không'}")
            
            # Kiểm tra tính đúng đắn của lời giải
            test_state = astar_state.copy()
            for move in astar_path:
                test_state = test_state.apply_move(move, MOVES_2x2)
            
            if test_state == state:
                print(f"✓ Lời giải A* hoạt động đúng!")
            else:
                print(f"✗ LỖI: Lời giải A* KHÔNG hoạt động đúng!")
                print(f"  CP = {test_state.cp}, CO = {test_state.co}")
        else:
            print("Không tìm thấy lời giải bằng A*!")
            
        # Kiểm tra lời giải trực tiếp
        print("\nKiểm tra lời giải dự kiến:")
        test_state = Rubik2x2State(scrambled_state.cp, scrambled_state.co)
        for move in expected_solution:
            test_state = test_state.apply_move(move, MOVES_2x2)
        
        if test_state == state:
            print(f"✓ Lời giải dự kiến hoạt động đúng!")
        else:
            print(f"✗ LỖI: Lời giải dự kiến KHÔNG hoạt động đúng!")
            print(f"  CP = {test_state.cp}, CO = {test_state.co}")

def test_direct_vs_algorithms():
    """So sánh trạng thái tạo ra khi áp dụng công thức và lời giải của thuật toán"""
    print("\n=== SO SÁNH TRẠNG THÁI TẠO RA BẰNG CÔNG THỨC VÀ LỜI GIẢI ===")
    
    # Trạng thái ban đầu
    state = SOLVED_STATE_2x2.copy()
    
    # Công thức cần kiểm tra
    formula = ["R", "U", "R'", "U'", "R'", "F", "R", "F'"]
    print(f"Công thức: {' '.join(formula)}")
    
    # Áp dụng công thức
    scrambled_state = state.copy()
    print("\nTrạng thái sau mỗi bước của công thức:")
    current_state = state.copy()
    for i, move in enumerate(formula):
        current_state = current_state.apply_move(move, MOVES_2x2)
        print(f"  Sau {move}: CP={current_state.cp}, CO={current_state.co}")
    
    # Lưu trạng thái sau khi áp dụng công thức
    final_direct_state = current_state.copy()
    
    # Tìm lời giải bằng BFS
    print("\nTìm lời giải bằng BFS:")
    bfs_state = Rubik2x2State(scrambled_state.cp, scrambled_state.co)
    bfs_path, bfs_nodes, bfs_time = a_star(bfs_state, time_limit=60)
    
    if bfs_path:
        print(f"Lời giải BFS: {' '.join(bfs_path)}")
        
        # Áp dụng lời giải BFS
        print("\nTrạng thái sau mỗi bước của lời giải BFS:")
        current_state = bfs_state.copy()
        for i, move in enumerate(bfs_path):
            current_state = current_state.apply_move(move, MOVES_2x2)
            print(f"  Sau {move}: CP={current_state.cp}, CO={current_state.co}")
        
        # Lưu trạng thái sau khi áp dụng lời giải
        final_bfs_state = current_state.copy()
        
        # So sánh trạng thái ban đầu, sau khi áp dụng công thức và sau khi áp dụng lời giải
        print("\nSo sánh các trạng thái:")
        print(f"Trạng thái ban đầu:         CP={state.cp}, CO={state.co}")
        print(f"Sau khi áp dụng công thức:  CP={bfs_state.cp}, CO={bfs_state.co}")
        print(f"Sau khi áp dụng lời giải:   CP={final_bfs_state.cp}, CO={final_bfs_state.co}")
        
        # Kiểm tra tính đúng đắn
        if final_bfs_state == state:
            print("✓ Lời giải BFS đưa về trạng thái ban đầu!")
        else:
            print("✗ LỖI: Lời giải BFS KHÔNG đưa về trạng thái ban đầu!")
    else:
        print("Không tìm thấy lời giải bằng BFS!")
    
    # Tìm lời giải bằng A*
    print("\nTìm lời giải bằng A*:")
    astar_state = Rubik2x2State(scrambled_state.cp, scrambled_state.co)
    astar_path, astar_nodes, astar_time = a_star(astar_state, time_limit=60)
    
    if astar_path:
        print(f"Lời giải A*: {' '.join(astar_path)}")
        
        # Áp dụng lời giải A*
        print("\nTrạng thái sau mỗi bước của lời giải A*:")
        current_state = astar_state.copy()
        for i, move in enumerate(astar_path):
            current_state = current_state.apply_move(move, MOVES_2x2)
            print(f"  Sau {move}: CP={current_state.cp}, CO={current_state.co}")
        
        # Lưu trạng thái sau khi áp dụng lời giải
        final_astar_state = current_state.copy()
        
        # So sánh trạng thái ban đầu, sau khi áp dụng công thức và sau khi áp dụng lời giải
        print("\nSo sánh các trạng thái:")
        print(f"Trạng thái ban đầu:         CP={state.cp}, CO={state.co}")
        print(f"Sau khi áp dụng công thức:  CP={astar_state.cp}, CO={astar_state.co}")
        print(f"Sau khi áp dụng lời giải:   CP={final_astar_state.cp}, CO={final_astar_state.co}")
        
        # Kiểm tra tính đúng đắn
        if final_astar_state == state:
            print("✓ Lời giải A* đưa về trạng thái ban đầu!")
        else:
            print("✗ LỖI: Lời giải A* KHÔNG đưa về trạng thái ban đầu!")
    else:
        print("Không tìm thấy lời giải bằng A*!")

def main():
    print("=== BẮT ĐẦU KIỂM TRA RUBIK 2X2 ===")
    
    
    
    # Kiểm tra tính nhất quán của các phép xoay
    test_move_consistency()
    
    # Kiểm tra định nghĩa phép xoay
    test_move_definitions()
    
    # Kiểm tra các thuật toán nổi tiếng
    test_algorithms()
    
    # Kiểm tra áp dụng đường đi xuôi và ngược
    test_bidirectional_moves()
    
    # Kiểm tra hàm heuristic
    test_heuristic()
    
    # Kiểm tra các phương thức của lớp
    test_class_methods()
    
    # Kiểm tra các thuật toán tìm kiếm với độ sâu tăng dần
    test_search_algorithms(max_depth=5)
    
    # Kiểm tra các công thức xáo trộn phức tạp
    test_complex_scrambles()
    
    print("\n=== KẾT THÚC KIỂM TRA RUBIK 2X2 ===")

if __name__ == "__main__":
    main()
