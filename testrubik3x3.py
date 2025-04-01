from RubikState.rubik_chen import RubikState, SOLVED_STATE_3x3, MOVES_3x3, heuristic_3x3
from RubikState.rubik_solver import bfs, a_star, ida_star
import time
import random
import copy

def test_move_consistency():
    """Kiểm tra tính nhất quán của các phép xoay"""
    print("\n=== KIỂM TRA TÍNH NHẤT QUÁN CỦA CÁC PHÉP XOAY ===")
    
    state = SOLVED_STATE_3x3.copy()
    
    # Kiểm tra từng phép xoay và phép ngược của nó
    for move in MOVES_3x3.keys():
        if move.endswith("'"):  # Bỏ qua các phép ngược vì sẽ kiểm tra chúng theo cặp
            continue
            
        move_prime = move + "'"
        
        # Áp dụng phép xoay và phép ngược của nó
        test_state = state.copy()
        test_state = test_state.apply_move(move, MOVES_3x3)
        test_state = test_state.apply_move(move_prime, MOVES_3x3)
        
        if test_state == state:
            print(f"✓ {move} và {move_prime} hoạt động đúng (trở về trạng thái ban đầu)")
        else:
            print(f"✗ LỖI: {move} và {move_prime} KHÔNG trở về trạng thái ban đầu!")
            print(f"  Ban đầu: CP={state.cp}, CO={state.co}, EP={state.ep}, EO={state.eo}")
            print(f"  Sau khi áp dụng: CP={test_state.cp}, CO={test_state.co}, EP={test_state.ep}, EO={test_state.eo}")
            
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
                test_state = test_state.apply_move(move, MOVES_3x3)
                
        if test_state == state:
            print(f"✓ {name} x2 hoạt động đúng (trở về ban đầu sau 2 lần)")
        else:
            print(f"✗ LỖI: {name} x2 KHÔNG trở về trạng thái ban đầu sau 2 lần!")
    
    # Kiểm tra phép xoay 4 lần
    for move in ["R", "U", "F", "L", "D", "B"]:
        # Áp dụng phép xoay 4 lần sẽ trở về ban đầu
        test_state = state.copy()
        for _ in range(4):
            test_state = test_state.apply_move(move, MOVES_3x3)
            
        if test_state == state:
            print(f"✓ {move} x4 hoạt động đúng (trở về ban đầu sau 4 lần)")
        else:
            print(f"✗ LỖI: {move} x4 KHÔNG trở về trạng thái ban đầu sau 4 lần!")

def test_algorithms():
    """Kiểm tra các thuật toán nổi tiếng có hoạt động đúng không"""
    print("\n=== KIỂM TRA CÁC THUẬT TOÁN NỔI TIẾNG ===")
    
    state = SOLVED_STATE_3x3.copy()
    
    # Kiểm tra sexy move (R U R' U') x6 = trạng thái ban đầu
    sexy_move = ["R", "U", "R'", "U'"]
    test_state = state.copy()
    
    print("Sexy move (R U R' U') x6:")
    for i in range(6):
        for move in sexy_move:
            test_state = test_state.apply_move(move, MOVES_3x3)
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
                temp_state = temp_state.apply_move(move, MOVES_3x3)
        print(f"  Sune x{i}: {'Khớp' if temp_state == state else 'Không khớp'} với trạng thái ban đầu")
    
    # Kiểm tra thuật toán T perm
    t_perm = ["R", "U", "R'", "U'", "R'", "F", "R", "R", "U'", "R'", "U'", "R", "U", "R'", "F'"]
    test_state = state.copy()
    
    print("\nT Perm:")
    # Áp dụng T Perm 2 lần sẽ trở về ban đầu
    for move in t_perm:
        test_state = test_state.apply_move(move, MOVES_3x3)
        
    print(f"  T Perm x1: {'Không khớp' if test_state != state else 'Khớp'} với trạng thái ban đầu (nên khác)")
    
    for move in t_perm:
        test_state = test_state.apply_move(move, MOVES_3x3)
        
    print(f"  T Perm x2: {'Khớp' if test_state == state else 'Không khớp'} với trạng thái ban đầu (nên giống)")

def test_bidirectional_moves():
    """Kiểm tra việc áp dụng đường đi xuôi và ngược"""
    print("\n=== KIỂM TRA ÁP DỤNG ĐƯỜNG ĐI XUÔI VÀ NGƯỢC ===")
    
    # Tạo một chuỗi nước đi ngẫu nhiên
    moves = ["R", "U", "F", "L", "D", "B", "R'", "U'", "F'", "L'", "D'", "B'"]
    scramble = random.choices(moves, k=8)
    
    print(f"Chuỗi xáo trộn: {' '.join(scramble)}")
    
    # Áp dụng chuỗi xáo trộn
    state = SOLVED_STATE_3x3.copy()
    scrambled_state = state.copy()
    
    print("\nÁp dụng từng nước đi:")
    for i, move in enumerate(scramble):
        scrambled_state = scrambled_state.apply_move(move, MOVES_3x3)
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
        recovered_state = recovered_state.apply_move(move, MOVES_3x3)
        print(f"  Bước {i+1}: {move}")
    
    # So sánh kết quả
    if recovered_state == state:
        print("✓ Áp dụng đường đi ngược hoạt động đúng (trở về trạng thái ban đầu)!")
    else:
        print("✗ LỖI: Áp dụng đường đi ngược KHÔNG trở về trạng thái ban đầu!")
        print(f"  Trạng thái ban đầu: CP={state.cp}, CO={state.co}, EP={state.ep}, EO={state.eo}")
        print(f"  Trạng thái sau khi áp dụng đường đi ngược: CP={recovered_state.cp}, CO={recovered_state.co}, EP={recovered_state.ep}, EO={recovered_state.eo}")

def test_heuristic():
    """Kiểm tra hàm heuristic"""
    print("\n=== KIỂM TRA HÀM HEURISTIC ===")
    
    state = SOLVED_STATE_3x3.copy()
    
    # Kiểm tra heuristic của trạng thái đã giải
    h = heuristic_3x3(state)
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
            test_state = test_state.apply_move(move, MOVES_3x3)
        
        h = heuristic_3x3(test_state)
        print(f"Heuristic sau {len(moves)} nước đi ({' '.join(moves) if moves else 'không có'}): {h}")


def test_class_methods():
    """Kiểm tra các phương thức của lớp RubikState"""
    print("\n=== KIỂM TRA CÁC PHƯƠNG THỨC CỦA LỚP RUBIKSTATE ===")
    
    # Tạo một trạng thái đã giải
    state = SOLVED_STATE_3x3.copy()
    
    # Kiểm tra phương thức copy
    state_copy = state.copy()
    print(f"Copy đúng? {'Đúng' if state == state_copy else 'Sai'}")
    
    # Kiểm tra phương thức __eq__
    print("\nKiểm tra __eq__:")
    state1 = RubikState(state.cp, state.co, state.ep, state.eo)
    state2 = RubikState(state.cp, state.co, state.ep, state.eo)
    print(f"  Hai trạng thái giống nhau: {state1 == state2}")
    
    # Thay đổi một chút
    state2 = RubikState(state.cp, state.co, state.ep, state.eo)
    state2 = state2.apply_move("R", MOVES_3x3)
    print(f"  Hai trạng thái khác nhau: {state1 != state2}")
    
    # Kiểm tra phương thức __hash__
    print("\nKiểm tra __hash__:")
    state_set = {state1, state2}
    print(f"  Số phần tử trong set: {len(state_set)} (nên là 2)")
    
    # Kiểm tra hash của trạng thái đã giải
    print(f"  Hash của trạng thái đã giải: {hash(state1)}")

def test_complex_scrambles():
    """Kiểm tra các công thức xáo trộn phức tạp hơn"""
    print("\n=== KIỂM TRA CÁC CÔNG THỨC XÁO TRỘN PHỨC TẠP ===")
    
    state = SOLVED_STATE_3x3.copy()
    
    # Danh sách các chuỗi xáo trộn phức tạp
    complex_scrambles = [
        ["R", "U", "R'", "U'", "R'", "F", "R", "F'"],  # OLL - Oriented Last Layer
        ["R", "U'", "R", "U", "R", "U", "R", "U'", "R'", "U'", "R", "R"],  # U-perm
        ["R", "L", "U", "U", "R'", "L'", "F", "F"],  # Công thức xáo trộn phức tạp hơn
    ]
    
    for i, scramble in enumerate(complex_scrambles):
        print(f"\nCông thức phức tạp {i+1}: {' '.join(scramble)}")
        
        # Áp dụng chuỗi xáo trộn
        scrambled_state = state.copy()
        for move in scramble:
            scrambled_state = scrambled_state.apply_move(move, MOVES_3x3)
        
        # So sánh với trạng thái đã giải
        if scrambled_state == state:
            print("  Cảnh báo: Công thức đã quay về trạng thái đã giải!")
            continue
        
        # Tìm kiếm lời giải bằng BFS
        print("  Tìm lời giải bằng BFS:")
        bfs_state = RubikState(scrambled_state.cp, scrambled_state.co, scrambled_state.ep, scrambled_state.eo)
        start_time = time.time()
        bfs_path, bfs_nodes, bfs_time = bfs(bfs_state, time_limit=120)
        
        if bfs_path:
            print(f"  Tìm thấy lời giải trong {bfs_time:.4f}s, {bfs_nodes} nút đã duyệt")
            print(f"  Độ dài lời giải: {len(bfs_path)}")
            print(f"  Lời giải: {' '.join(bfs_path)}")
            
            # Kiểm tra tính đúng đắn của lời giải
            test_state = bfs_state.copy()
            for move in bfs_path:
                test_state = test_state.apply_move(move, MOVES_3x3)
            
            if test_state == state:
                print("  ✓ Lời giải hoạt động đúng!")
            else:
                print("  ✗ LỖI: Lời giải KHÔNG đưa về trạng thái đã giải!")
        else:
            print("  Không tìm thấy lời giải trong thời gian cho phép!")
            
        # Thử A* cho trường hợp đầu tiên
        if i == 0:
            print("\n  Thử A* cho công thức này:")
            astar_state = RubikState(scrambled_state.cp, scrambled_state.co, scrambled_state.ep, scrambled_state.eo)
            astar_path, astar_nodes, astar_time = a_star(astar_state, time_limit=60)
            
            if astar_path:
                print(f"  Tìm thấy lời giải trong {astar_time:.4f}s, {astar_nodes} nút đã duyệt")
                print(f"  Độ dài lời giải: {len(astar_path)}")
                print(f"  Lời giải: {' '.join(astar_path)}")
                
                # Kiểm tra tính đúng đắn của lời giải
                test_state = astar_state.copy()
                for move in astar_path:
                    test_state = test_state.apply_move(move, MOVES_3x3)
                
                if test_state == state:
                    print("  ✓ Lời giải A* hoạt động đúng!")
                else:
                    print("  ✗ LỖI: Lời giải A* KHÔNG đưa về trạng thái đã giải!")
            else:
                print("  Không tìm thấy lời giải bằng A* trong thời gian cho phép!")

def test_search_algorithms(max_depth=5):
    """Kiểm tra các thuật toán tìm kiếm với độ sâu tăng dần"""
    print(f"\n=== KIỂM TRA CÁC THUẬT TOÁN TÌM KIẾM (tối đa {max_depth} nước) ===")
    
    state = SOLVED_STATE_3x3.copy()
    
    for depth in range(1, max_depth + 1):
        print(f"\n--- Độ sâu {depth} ---")
        
        # Tạo một chuỗi xáo trộn ngẫu nhiên với độ sâu đã chọn
        moves = ["R", "U", "F", "L", "D", "B", "R'", "U'", "F'", "L'", "D'", "B'"]
        scramble = random.choices(moves, k=depth)
        
        print(f"Chuỗi xáo trộn: {' '.join(scramble)}")
        
        # Áp dụng chuỗi xáo trộn
        scrambled_state = state.copy()
        for move in scramble:
            scrambled_state = scrambled_state.apply_move(move, MOVES_3x3)
        
        # Lưu trữ chuỗi xáo trộn ngược để so sánh
        reverse_scramble = []
        for move in reversed(scramble):
            if "'" in move:
                reverse_scramble.append(move.replace("'", ""))
            else:
                reverse_scramble.append(move + "'")
        
        # Kiểm tra thuật toán BFS
        print("\nKiểm tra BFS:")
        bfs_state = RubikState(scrambled_state.cp, scrambled_state.co, scrambled_state.ep, scrambled_state.eo)
        start_time = time.time()
        bfs_path, bfs_nodes, bfs_time = bfs(bfs_state, time_limit=60)
        print(f"  Thời gian: {bfs_time:.4f}s, Số nút đã duyệt: {bfs_nodes}")
        
        if bfs_path:
            print(f"  Độ dài lời giải: {len(bfs_path)}")
            print(f"  Lời giải: {' '.join(bfs_path)}")
            
            # Kiểm tra xem lời giải có đúng không
            test_state = bfs_state.copy()
            for move in bfs_path:
                test_state = test_state.apply_move(move, MOVES_3x3)
            
            if test_state == state:
                print("  ✓ Lời giải BFS hoạt động đúng!")
            else:
                print("  ✗ LỖI: Lời giải BFS KHÔNG đưa về trạng thái đã giải!")
                
                # Thử đảo ngược lời giải
                print("  Thử nghiệm đảo ngược lời giải BFS:")
                test_state = bfs_state.copy()
                for move in reversed(bfs_path):
                    if "'" in move:
                        inverse_move = move.replace("'", "")
                    else:
                        inverse_move = move + "'"
                    test_state = test_state.apply_move(inverse_move, MOVES_3x3)
                
                if test_state == state:
                    print("  ✓ Lời giải đảo ngược hoạt động đúng!")
                else:
                    print("  ✗ Lời giải đảo ngược cũng KHÔNG đúng!")
        else:
            print("  Không tìm thấy lời giải bằng BFS!")
        
        # Kiểm tra thuật toán A*
        print("\nKiểm tra A*:")
        astar_state = RubikState(scrambled_state.cp, scrambled_state.co, scrambled_state.ep, scrambled_state.eo)
        start_time = time.time()
        astar_path, astar_nodes, astar_time = a_star(astar_state, time_limit=60)
        print(f"  Thời gian: {astar_time:.4f}s, Số nút đã duyệt: {astar_nodes}")
        
        if astar_path:
            print(f"  Độ dài lời giải: {len(astar_path)}")
            print(f"  Lời giải: {' '.join(astar_path)}")
            
            # Kiểm tra xem lời giải có đúng không
            test_state = astar_state.copy()
            for move in astar_path:
                test_state = test_state.apply_move(move, MOVES_3x3)
            
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
                    test_state = test_state.apply_move(inverse_move, MOVES_3x3)
                
                if test_state == state:
                    print("  ✓ Lời giải đảo ngược hoạt động đúng!")
                else:
                    print("  ✗ Lời giải đảo ngược cũng KHÔNG đúng!")
        else:
            print("  Không tìm thấy lời giải bằng A*!")
        
        # Kiểm tra thuật toán IDA*
        print("\nKiểm tra IDA*:")
        ida_state = RubikState(scrambled_state.cp, scrambled_state.co, scrambled_state.ep, scrambled_state.eo)
        start_time = time.time()
        ida_path, ida_nodes, ida_time = ida_star(ida_state, time_limit=60)
        print(f"  Thời gian: {ida_time:.4f}s, Số nút đã duyệt: {ida_nodes}")
        
        if ida_path:
            print(f"  Độ dài lời giải: {len(ida_path)}")
            print(f"  Lời giải: {' '.join(ida_path)}")
            
            # Kiểm tra xem lời giải có đúng không
            test_state = ida_state.copy()
            for move in ida_path:
                test_state = test_state.apply_move(move, MOVES_3x3)
            
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
                    test_state = test_state.apply_move(inverse_move, MOVES_3x3)
                
                if test_state == state:
                    print("  ✓ Lời giải đảo ngược hoạt động đúng!")
                else:
                    print("  ✗ Lời giải đảo ngược cũng KHÔNG đúng!")
        else:
            print("  Không tìm thấy lời giải bằng IDA*!")

def test_edge_only_scrambles():
    """Kiểm tra trường hợp chỉ xáo trộn các cạnh"""
    print("\n=== KIỂM TRA TRƯỜNG HỢP CHỈ XÁO TRỘN CÁC CẠNH ===")
    
    state = SOLVED_STATE_3x3.copy()
    
    # Danh sách các chuỗi xáo trộn chỉ ảnh hưởng đến cạnh
    # Thay thế M, E, S bằng các phép xoay cơ bản
    edge_scrambles = [
        # Thay thế "M U M' U'" bằng "L' R U L R' U'" - Tương đương tầng giữa xoay
        ["L'", "R", "U", "L", "R'", "U'"],
        
        # Thay thế "M M U M M U U" bằng "F B' R R L L U F' B R R L L U U" - Tương đương H-perm
        ["R", "U", "R'", "U", "R", "U", "U", "R'", "L'", "U'", "L", "U'", "L'", "U", "U", "L"],
        
        # Z-perm (phép hoán vị trên mặt U)
        ["R", "U", "R'", "U", "R'", "U'", "R'", "U'", "R'", "U", "R'"]
    ]
    
    for i, scramble in enumerate(edge_scrambles):
        print(f"\nChuỗi xáo trộn cạnh {i+1}: {' '.join(scramble)}")
        
        # Áp dụng chuỗi xáo trộn
        scrambled_state = state.copy()
        for move in scramble:
            scrambled_state = scrambled_state.apply_move(move, MOVES_3x3)
        
        # Kiểm tra xem góc có bị ảnh hưởng không
        corners_changed = False
        if i == 0:  # Chỉ kiểm tra cho công thức đầu tiên, vì các công thức khác có thể ảnh hưởng đến góc
            corners_changed = (scrambled_state.cp != state.cp) or (scrambled_state.co != state.co)
            print(f"  Góc có bị thay đổi: {'Có' if corners_changed else 'Không'}")
        
        # Kiểm tra xem cạnh có bị ảnh hưởng không
        edges_changed = (scrambled_state.ep != state.ep) or (scrambled_state.eo != state.eo)
        print(f"  Cạnh có bị thay đổi: {'Có' if edges_changed else 'Không'} (nên là Có)")
        
        # Tìm kiếm lời giải bằng BFS
        print("  Tìm lời giải bằng BFS:")
        bfs_state = RubikState(scrambled_state.cp, scrambled_state.co, scrambled_state.ep, scrambled_state.eo)
        start_time = time.time()
        bfs_path, bfs_nodes, bfs_time = bfs(bfs_state, time_limit=120)
        
        if bfs_path:
            print(f"  Tìm thấy lời giải trong {bfs_time:.4f}s, {bfs_nodes} nút đã duyệt")
            print(f"  Độ dài lời giải: {len(bfs_path)}")
            print(f"  Lời giải: {' '.join(bfs_path)}")
            
            # Kiểm tra tính đúng đắn của lời giải
            test_state = bfs_state.copy()
            for move in bfs_path:
                test_state = test_state.apply_move(move, MOVES_3x3)
            
            if test_state == state:
                print("  ✓ Lời giải hoạt động đúng!")
            else:
                print("  ✗ LỖI: Lời giải KHÔNG đưa về trạng thái đã giải!")
        else:
            print("  Không tìm thấy lời giải trong thời gian cho phép!")

def test_corner_only_scrambles():
    """Kiểm tra trường hợp chỉ xáo trộn các góc"""
    print("\n=== KIỂM TRA TRƯỜNG HỢP CHỈ XÁO TRỘN CÁC GÓC ===")
    
    state = SOLVED_STATE_3x3.copy()
    
    # Danh sách các chuỗi xáo trộn chỉ ảnh hưởng đến góc
    corner_scrambles = [
        ["R", "U", "R'", "U'"],  # Sexy move
        ["R", "U", "R'", "U", "R", "U", "U", "R'"],  # Sune
        ["R", "U'", "L'", "U", "R'", "U'", "L"],  # Niklas
    ]
    
    for i, scramble in enumerate(corner_scrambles):
        print(f"\nChuỗi xáo trộn góc {i+1}: {' '.join(scramble)}")
        
        # Áp dụng chuỗi xáo trộn
        scrambled_state = state.copy()
        for move in scramble:
            scrambled_state = scrambled_state.apply_move(move, MOVES_3x3)
        
        # Kiểm tra xem góc có bị ảnh hưởng không
        corners_changed = (scrambled_state.cp != state.cp) or (scrambled_state.co != state.co)
        print(f"  Góc có bị thay đổi: {'Có' if corners_changed else 'Không'} (nên là Có)")
        
        # Tìm kiếm lời giải bằng BFS
        print("  Tìm lời giải bằng BFS:")
        bfs_state = RubikState(scrambled_state.cp, scrambled_state.co, scrambled_state.ep, scrambled_state.eo)
        start_time = time.time()
        bfs_path, bfs_nodes, bfs_time = bfs(bfs_state, time_limit=120)
        
        if bfs_path:
            print(f"  Tìm thấy lời giải trong {bfs_time:.4f}s, {bfs_nodes} nút đã duyệt")
            print(f"  Độ dài lời giải: {len(bfs_path)}")
            print(f"  Lời giải: {' '.join(bfs_path)}")
            
            # Kiểm tra tính đúng đắn của lời giải
            test_state = bfs_state.copy()
            for move in bfs_path:
                test_state = test_state.apply_move(move, MOVES_3x3)
            
            if test_state == state:
                print("  ✓ Lời giải hoạt động đúng!")
            else:
                print("  ✗ LỖI: Lời giải KHÔNG đưa về trạng thái đã giải!")
        else:
            print("  Không tìm thấy lời giải trong thời gian cho phép!")

def test_long_formula_with_inverse():
    """Kiểm tra công thức dài và phép ngược của nó"""
    print("\n=== KIỂM TRA CÔNG THỨC DÀI VÀ PHÉP NGƯỢC CỦA NÓ ===")
    
    state = SOLVED_STATE_3x3.copy()
    
    # Công thức dài gồm 18 phép xoay (tất cả các mặt và phép nghịch đảo)
    long_formula = ["R", "U", "F", "D", "L", "B", "R'", "U'", "F'", "D'", "L'", "B'", "R", "U", "F", "D", "L", "B"]
    print(f"Công thức gốc: {' '.join(long_formula)}")
    
    # Áp dụng công thức gốc
    scrambled_state = state.copy()
    print("\nÁp dụng công thức gốc:")
    for i, move in enumerate(long_formula):
        scrambled_state = scrambled_state.apply_move(move, MOVES_3x3)
        print(f"  Bước {i+1}: {move}")
    
    # Tạo công thức ngược
    inverse_formula = []
    for move in reversed(long_formula):
        if "'" in move:
            inverse_formula.append(move.replace("'", ""))
        else:
            inverse_formula.append(move + "'")
    
    print(f"\nCông thức ngược: {' '.join(inverse_formula)}")
    
    # Áp dụng công thức ngược
    recovered_state = scrambled_state.copy()
    print("\nÁp dụng công thức ngược:")
    for i, move in enumerate(inverse_formula):
        recovered_state = recovered_state.apply_move(move, MOVES_3x3)
        print(f"  Bước {i+1}: {move}")
    
    # So sánh kết quả
    if recovered_state == state:
        print("✓ Áp dụng công thức ngược hoạt động đúng (trở về trạng thái ban đầu)!")
    else:
        print("✗ LỖI: Áp dụng công thức ngược KHÔNG trở về trạng thái ban đầu!")
        print(f"  Trạng thái ban đầu: CP={state.cp}, CO={state.co}, EP={state.ep}, EO={state.eo}")
        print(f"  Trạng thái sau khi áp dụng công thức ngược: CP={recovered_state.cp}, CO={recovered_state.co}, EP={recovered_state.ep}, EO={recovered_state.eo}")
    
    # Nếu không trở về đúng, thử kiểm tra xem lỗi xuất hiện ở nước nào
    if recovered_state != state:
        print("\nKiểm tra chi tiết từng bước trong công thức ngược để xác định lỗi:")
        check_state = scrambled_state.copy()
        for i, move in enumerate(inverse_formula):
            prev_state = check_state.copy()
            check_state = check_state.apply_move(move, MOVES_3x3)
            
            # Kiểm tra phép xoay cơ bản tương ứng
            basic_move = move.replace("'", "") if "'" in move else move + "'"
            test_state = prev_state.copy()
            test_state = test_state.apply_move(basic_move, MOVES_3x3)
            test_state = test_state.apply_move(move, MOVES_3x3)
            
            if test_state == prev_state:
                print(f"  Bước {i+1}: {move} hoạt động đúng như phép ngược của {basic_move}")
            else:
                print(f"  Bước {i+1}: {move} KHÔNG hoạt động đúng như phép ngược của {basic_move}!")
                print(f"    Trạng thái trước: CP={prev_state.cp}, CO={prev_state.co}")
                print(f"    Sau khi áp dụng {basic_move} rồi {move}: CP={test_state.cp}, CO={test_state.co}")

def test_state_representation_consistency():
    """Kiểm tra tính nhất quán của biểu diễn trạng thái"""
    print("\n=== KIỂM TRA TÍNH NHẤT QUÁN CỦA BIỂU DIỄN TRẠNG THÁI ===")
    
    # Import các thành phần cần thiết
    from RubikState.rubik_chen import RubikState, SOLVED_STATE_3x3, MOVES_3x3
    from RubikState.rubik_2x2 import Rubik2x2State, SOLVED_STATE_2x2, MOVES_2x2
    
    # ===== KIỂM TRA TÍNH NHẤT QUÁN CỦA RUBIK 3X3 =====
    print("\n1. KIỂM TRA TÍNH NHẤT QUÁN CỦA RUBIK 3X3:")
    
    # Kiểm tra xem phép áp dụng một nước đi và phép ngược của nó có trở về trạng thái ban đầu không
    state_3x3 = SOLVED_STATE_3x3.copy()
    
    # Tạo các trạng thái khác nhau từ các phép xoay khác nhau
    sequences = [
        ["R", "U", "R'", "U'"],  # sexy move
        ["F", "R", "U", "R'", "U'", "F'"],  # phép OLL đơn giản
        ["R", "U", "R'", "U", "R", "U", "U", "R'"],  # Sune
    ]
    
    for seq in sequences:
        print(f"\nKiểm tra chuỗi: {' '.join(seq)}")
        
        # Tạo 2 trạng thái giống nhau
        state1 = state_3x3.copy()
        state2 = state_3x3.copy()
        
        # Áp dụng cùng chuỗi nước đi trên cả 2 trạng thái
        for move in seq:
            state1 = state1.apply_move(move, MOVES_3x3)
        
        # Áp dụng từng nước một
        for move in seq:
            state2 = state2.apply_move(move, MOVES_3x3)
        
        # So sánh 2 trạng thái
        if state1 == state2:
            print(f"  ✓ Hai cách áp dụng chuỗi nước đi cho kết quả giống nhau")
        else:
            print(f"  ✗ LỖI: Hai cách áp dụng chuỗi nước đi cho kết quả KHÁC NHAU!")
            print(f"  Trạng thái 1: CP={state1.cp}, CO={state1.co}, EP={state1.ep}, EO={state1.eo}")
            print(f"  Trạng thái 2: CP={state2.cp}, CO={state2.co}, EP={state2.ep}, EO={state2.eo}")
    
    # ===== KIỂM TRA TÍNH NHẤT QUÁN CỦA RUBIK 2X2 =====
    print("\n2. KIỂM TRA TÍNH NHẤT QUÁN CỦA RUBIK 2X2:")
    
    # Kiểm tra xem phép áp dụng một nước đi và phép ngược của nó có trở về trạng thái ban đầu không
    state_2x2 = SOLVED_STATE_2x2.copy()
    
    # Tạo các trạng thái khác nhau từ các phép xoay khác nhau
    sequences_2x2 = [
        ["R", "U", "R'", "U'"],  # sexy move
        ["R", "U", "R'", "U", "R", "U", "U", "R'"],  # Sune
        ["F", "R", "U", "R'", "U'", "F'"],  # OLL đơn giản
    ]
    
    for seq in sequences_2x2:
        print(f"\nKiểm tra chuỗi trên Rubik 2x2: {' '.join(seq)}")
        
        # Tạo 2 trạng thái giống nhau
        state1 = state_2x2.copy()
        state2 = state_2x2.copy()
        
        # Áp dụng cùng chuỗi nước đi trên cả 2 trạng thái
        for move in seq:
            state1 = state1.apply_move(move, MOVES_2x2)
        
        # Áp dụng từng nước một
        for move in seq:
            state2 = state2.apply_move(move, MOVES_2x2)
        
        # So sánh 2 trạng thái
        if state1 == state2:
            print(f"  ✓ Hai cách áp dụng chuỗi nước đi cho kết quả giống nhau")
        else:
            print(f"  ✗ LỖI: Hai cách áp dụng chuỗi nước đi cho kết quả KHÁC NHAU!")
            print(f"  Trạng thái 1: CP={state1.cp}, CO={state1.co}")
            print(f"  Trạng thái 2: CP={state2.cp}, CO={state2.co}")
    
    # ===== SO SÁNH BIỂU DIỄN GIỮA RUBIK 3X3 VÀ 2X2 =====
    print("\n3. SO SÁNH BIỂU DIỄN GIỮA RUBIK 3X3 VÀ 2X2:")
    
    # Khối góc trên Rubik 3x3 và 2x2 nên hoạt động giống nhau
    # Tạo cùng một chuỗi nước đi cho cả hai
    test_sequences = [
        ["R", "U", "R'", "U'"],  # sexy move
        ["U", "R", "U'", "R'"],  # inverse sexy move
        ["F", "R", "U", "R'", "U'", "F'"],  # OLL đơn giản
    ]
    
    for seq in test_sequences:
        print(f"\nSo sánh chuỗi: {' '.join(seq)}")
        
        # Áp dụng trên Rubik 3x3
        state_3x3 = SOLVED_STATE_3x3.copy()
        for move in seq:
            state_3x3 = state_3x3.apply_move(move, MOVES_3x3)
        
        # Áp dụng trên Rubik 2x2
        state_2x2 = SOLVED_STATE_2x2.copy()
        for move in seq:
            state_2x2 = state_2x2.apply_move(move, MOVES_2x2)
        
        # So sánh trạng thái của các góc
        corners_match = True
        for i in range(8):
            if state_3x3.cp[i] != state_2x2.cp[i] or state_3x3.co[i] != state_2x2.co[i]:
                corners_match = False
                break
        
        if corners_match:
            print(f"  ✓ Góc trên Rubik 3x3 và 2x2 hoạt động giống nhau")
        else:
            print(f"  ✗ LỖI: Góc trên Rubik 3x3 và 2x2 hoạt động KHÁC NHAU!")
            print(f"  3x3 - CP: {state_3x3.cp}, CO: {state_3x3.co}")
            print(f"  2x2 - CP: {state_2x2.cp}, CO: {state_2x2.co}")

def main():
    print("=== BẮT ĐẦU KIỂM TRA RUBIK 3X3 ===")
    
    # Thêm hàm kiểm tra mới
    test_state_representation_consistency()
    
    # Kiểm tra tính nhất quán của các phép xoay
    test_move_consistency()
    
    # Kiểm tra các thuật toán nổi tiếng
    test_algorithms()
    
    # Kiểm tra áp dụng đường đi xuôi và ngược
    test_bidirectional_moves()
    
    # Kiểm tra hàm heuristic
    test_heuristic()
    
    # Kiểm tra các phương thức của lớp
    test_class_methods()
    
    # Kiểm tra công thức dài và phép ngược của nó
    test_long_formula_with_inverse()
    
  
    # Kiểm tra các trường hợp xáo trộn phức tạp
    test_complex_scrambles()
    
    # Kiểm tra trường hợp chỉ xáo trộn các cạnh
    test_edge_only_scrambles()
    
    # Kiểm tra trường hợp chỉ xáo trộn các góc
    test_corner_only_scrambles()
    
    # Kiểm tra các thuật toán tìm kiếm với độ sâu tăng dần
    test_search_algorithms()
    
    print("\n=== KẾT THÚC KIỂM TRA RUBIK 3X3 ===")

if __name__ == "__main__":
    main()