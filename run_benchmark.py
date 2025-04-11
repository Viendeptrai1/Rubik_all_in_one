#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script benchmark để đánh giá hiệu suất các thuật toán tìm kiếm
trên Rubik 2x2 và 3x3 với các độ sâu xáo trộn khác nhau.
"""

import os
import time
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import random
import pickle

# Đảm bảo thư mục images tồn tại
os.makedirs('images', exist_ok=True)

# Import các module cần thiết
try:
    from RubikState.rubik_solver_2x2 import (
        a_star_search_2x2, bfs_search_2x2, dfs_search_2x2, 
        ida_star_search_2x2, ids_search_2x2, 
        greedy_best_first_search_2x2
    )
    from RubikState.rubik_solver_3x3 import (
        a_star_search_3x3, bfs_search_3x3, dfs_search_3x3, 
        ida_star_search_3x3, ids_search_3x3,
        greedy_best_first_search_3x3
    )
    from RubikState.rubik_2x2 import Rubik2x2State, SOLVED_STATE_2x2, MOVES_2x2, heuristic_2x2
    from RubikState.rubik_chen import RubikState, SOLVED_STATE_3x3, MOVES_3x3, heuristic_3x3
except ImportError as e:
    print(f"Lỗi khi import modules: {e}")
    print("Vui lòng đảm bảo bạn đang chạy script từ thư mục gốc của dự án.")
    exit(1)

# Nhóm 1: Các thuật toán không dùng thông tin (Uninformed Search)
UNINFORMED_ALGORITHMS_2x2 = {
    'BFS': lambda state, time_limit: bfs_search_2x2(state, SOLVED_STATE_2x2, MOVES_2x2, time_limit),
    'DFS': lambda state, time_limit: dfs_search_2x2(state, SOLVED_STATE_2x2, MOVES_2x2, time_limit, max_depth=10),
    'UCS': lambda state, time_limit: bfs_search_2x2(state, SOLVED_STATE_2x2, MOVES_2x2, time_limit),  # UCS = BFS với chi phí đều = 1
    'IDS': lambda state, time_limit: ids_search_2x2(state, SOLVED_STATE_2x2, MOVES_2x2, time_limit, max_depth=10)
}

UNINFORMED_ALGORITHMS_3x3 = {
    'BFS': lambda state, time_limit: bfs_search_3x3(state, SOLVED_STATE_3x3, MOVES_3x3, time_limit),
    'DFS': lambda state, time_limit: dfs_search_3x3(state, SOLVED_STATE_3x3, MOVES_3x3, time_limit, max_depth=10),
    'UCS': lambda state, time_limit: bfs_search_3x3(state, SOLVED_STATE_3x3, MOVES_3x3, time_limit),  # UCS = BFS với chi phí đều = 1
    'IDS': lambda state, time_limit: ids_search_3x3(state, SOLVED_STATE_3x3, MOVES_3x3, time_limit, max_depth=10)
}

# Nhóm 2: Các thuật toán dùng thông tin (Informed Search)
INFORMED_ALGORITHMS_2x2 = {
    'A*': lambda state, time_limit: a_star_search_2x2(state, SOLVED_STATE_2x2, MOVES_2x2, time_limit),
    'IDA*': lambda state, time_limit: ida_star_search_2x2(state, SOLVED_STATE_2x2, MOVES_2x2, time_limit),
    'Greedy Best-First': lambda state, time_limit: greedy_best_first_search_2x2(state, SOLVED_STATE_2x2, MOVES_2x2, time_limit)
}

INFORMED_ALGORITHMS_3x3 = {
    'A*': lambda state, time_limit: a_star_search_3x3(state, SOLVED_STATE_3x3, MOVES_3x3, time_limit),
    'IDA*': lambda state, time_limit: ida_star_search_3x3(state, SOLVED_STATE_3x3, MOVES_3x3, time_limit),
    'Greedy Best-First': lambda state, time_limit: greedy_best_first_search_3x3(state, SOLVED_STATE_3x3, MOVES_3x3, time_limit)
}

def scramble_cube_2x2(depth):
    """Xáo trộn khối Rubik 2x2 với độ sâu nhất định."""
    state = SOLVED_STATE_2x2
    moves = list(MOVES_2x2.keys())
    path = []
    
    for _ in range(depth):
        move = random.choice(moves)
        state = state.apply_move(move, MOVES_2x2)
        path.append(move)
    
    return state, path

def scramble_cube_3x3(depth):
    """Xáo trộn khối Rubik 3x3 với độ sâu nhất định."""
    state = SOLVED_STATE_3x3
    moves = list(MOVES_3x3.keys())
    path = []
    
    for _ in range(depth):
        move = random.choice(moves)
        state = state.apply_move(move, MOVES_3x3)
        path.append(move)
    
    return state, path

def run_benchmark(cube_size=2, max_depth=7, time_limit=20, num_trials=3):
    """
    Chạy benchmark cho các thuật toán trên khối Rubik với độ sâu khác nhau.
    
    Args:
        cube_size: Kích thước khối Rubik (2 hoặc 3)
        max_depth: Độ sâu xáo trộn tối đa
        time_limit: Thời gian tối đa cho mỗi thuật toán (giây)
        num_trials: Số lần thử nghiệm cho mỗi độ sâu
    
    Returns:
        times: Thời gian chạy trung bình cho mỗi thuật toán ở mỗi độ sâu
        nodes: Số nút duyệt trung bình cho mỗi thuật toán ở mỗi độ sâu
        success_rates: Tỉ lệ thành công cho mỗi thuật toán ở mỗi độ sâu
    """
    print(f"Chạy benchmark cho Rubik {cube_size}x{cube_size}...")
    
    # Chọn các thuật toán phù hợp
    if cube_size == 2:
        scramble_func = scramble_cube_2x2
        uninformed_algorithms = UNINFORMED_ALGORITHMS_2x2
        informed_algorithms = INFORMED_ALGORITHMS_2x2
    else:
        scramble_func = scramble_cube_3x3
        uninformed_algorithms = UNINFORMED_ALGORITHMS_3x3
        informed_algorithms = INFORMED_ALGORITHMS_3x3
    
    # Lưu kết quả
    times_uninformed = defaultdict(lambda: [float('inf')] * (max_depth + 1))
    nodes_uninformed = defaultdict(lambda: [0] * (max_depth + 1))
    success_uninformed = defaultdict(lambda: [0] * (max_depth + 1))
    
    times_informed = defaultdict(lambda: [float('inf')] * (max_depth + 1))
    nodes_informed = defaultdict(lambda: [0] * (max_depth + 1))
    success_informed = defaultdict(lambda: [0] * (max_depth + 1))
    
    # Chạy benchmark cho mỗi độ sâu
    for depth in range(1, max_depth + 1):
        print(f"\nĐộ sâu xáo trộn: {depth}")
        
        for trial in range(num_trials):
            print(f"  Thử nghiệm {trial + 1}/{num_trials}")
            
            # Tạo trạng thái xáo trộn
            scrambled_state, _ = scramble_func(depth)
            
            # Chạy các thuật toán không thông tin
            print("    Nhóm 1: Uninformed Search")
            for name, algo in uninformed_algorithms.items():
                print(f"      {name}: ", end="", flush=True)
                
                start_time = time.time()
                try:
                    result = algo(scrambled_state, time_limit)
                    if result and len(result) >= 2:  # (path, nodes, runtime)
                        path, nodes_visited, runtime = result
                        success = True
                        if depth <= 5:  # Dưới độ sâu 5, đảm bảo path được tìm thấy
                            assert path is not None
                    else:
                        success = False
                        nodes_visited = 0
                        runtime = time_limit
                except Exception as e:
                    print(f"Error: {e}")
                    success = False
                    nodes_visited = 0
                    runtime = time_limit
                
                # Lưu kết quả
                if success:
                    print(f"Thành công, thời gian: {runtime:.3f}s, số nút: {nodes_visited}")
                    # Lấy giá trị nhỏ hơn nếu đã có kết quả trước đó
                    times_uninformed[name][depth] = min(times_uninformed[name][depth], runtime)
                    # Lấy giá trị lớn hơn cho số nút
                    nodes_uninformed[name][depth] = max(nodes_uninformed[name][depth], nodes_visited)
                    success_uninformed[name][depth] += 1
                else:
                    print("Không tìm được lời giải trong thời gian giới hạn")
            
            # Chạy các thuật toán có thông tin
            print("    Nhóm 2: Informed Search")
            for name, algo in informed_algorithms.items():
                print(f"      {name}: ", end="", flush=True)
                
                start_time = time.time()
                try:
                    result = algo(scrambled_state, time_limit)
                    if result and len(result) >= 2:  # (path, nodes, runtime)
                        path, nodes_visited, runtime = result
                        success = True
                        if depth <= 5:  # Dưới độ sâu 5, đảm bảo path được tìm thấy
                            assert path is not None
                    else:
                        success = False
                        nodes_visited = 0
                        runtime = time_limit
                except Exception as e:
                    print(f"Error: {e}")
                    success = False
                    nodes_visited = 0
                    runtime = time_limit
                
                # Lưu kết quả
                if success:
                    print(f"Thành công, thời gian: {runtime:.3f}s, số nút: {nodes_visited}")
                    # Lấy giá trị nhỏ hơn nếu đã có kết quả trước đó
                    times_informed[name][depth] = min(times_informed[name][depth], runtime)
                    # Lấy giá trị lớn hơn cho số nút
                    nodes_informed[name][depth] = max(nodes_informed[name][depth], nodes_visited)
                    success_informed[name][depth] += 1
                else:
                    print("Không tìm được lời giải trong thời gian giới hạn")
    
    # Tính toán tỉ lệ thành công
    for name in uninformed_algorithms:
        for depth in range(1, max_depth + 1):
            success_uninformed[name][depth] /= num_trials
    
    for name in informed_algorithms:
        for depth in range(1, max_depth + 1):
            success_informed[name][depth] /= num_trials
    
    # Thay thế giá trị vô cực bằng None để không hiển thị trên biểu đồ
    for name in uninformed_algorithms:
        for depth in range(1, max_depth + 1):
            if times_uninformed[name][depth] == float('inf'):
                times_uninformed[name][depth] = None
    
    for name in informed_algorithms:
        for depth in range(1, max_depth + 1):
            if times_informed[name][depth] == float('inf'):
                times_informed[name][depth] = None
    
    return {
        'uninformed': {
            'times': times_uninformed,
            'nodes': nodes_uninformed,
            'success': success_uninformed
        },
        'informed': {
            'times': times_informed,
            'nodes': nodes_informed,
            'success': success_informed
        }
    }

def plot_results(results, cube_size, max_depth):
    """Vẽ biểu đồ kết quả benchmark."""
    depths = list(range(1, max_depth + 1))
    
    # Thiết lập font tiếng Việt
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans', 'Arial']
    plt.rcParams['axes.unicode_minus'] = False
    
    # === Vẽ biểu đồ cho nhóm 1: Uninformed Search ===
    # Biểu đồ thời gian chạy
    plt.figure(figsize=(10, 6))
    for name, times in results['uninformed']['times'].items():
        plt.plot(depths, times[1:], 'o-', label=name, linewidth=2)
    
    plt.title(f'Thời gian chạy các thuật toán Uninformed Search (Rubik {cube_size}x{cube_size})', fontsize=14)
    plt.xlabel('Độ sâu xáo trộn', fontsize=12)
    plt.ylabel('Thời gian (giây)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig(f'images/benchmark_time_uninformed_{cube_size}x{cube_size}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Biểu đồ số nút duyệt
    plt.figure(figsize=(10, 6))
    for name, nodes in results['uninformed']['nodes'].items():
        plt.plot(depths, nodes[1:], 'o-', label=name, linewidth=2)
    
    plt.title(f'Số nút duyệt của các thuật toán Uninformed Search (Rubik {cube_size}x{cube_size})', fontsize=14)
    plt.xlabel('Độ sâu xáo trộn', fontsize=12)
    plt.ylabel('Số nút duyệt', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig(f'images/benchmark_nodes_uninformed_{cube_size}x{cube_size}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Biểu đồ tỉ lệ thành công
    plt.figure(figsize=(10, 6))
    for name, success_rates in results['uninformed']['success'].items():
        plt.plot(depths, success_rates[1:], 'o-', label=name, linewidth=2)
    
    plt.title(f'Tỉ lệ thành công của các thuật toán Uninformed Search (Rubik {cube_size}x{cube_size})', fontsize=14)
    plt.xlabel('Độ sâu xáo trộn', fontsize=12)
    plt.ylabel('Tỉ lệ thành công', fontsize=12)
    plt.ylim(0, 1.05)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig(f'images/benchmark_success_uninformed_{cube_size}x{cube_size}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # === Vẽ biểu đồ cho nhóm 2: Informed Search ===
    # Biểu đồ thời gian chạy
    plt.figure(figsize=(10, 6))
    for name, times in results['informed']['times'].items():
        plt.plot(depths, times[1:], 'o-', label=name, linewidth=2)
    
    plt.title(f'Thời gian chạy các thuật toán Informed Search (Rubik {cube_size}x{cube_size})', fontsize=14)
    plt.xlabel('Độ sâu xáo trộn', fontsize=12)
    plt.ylabel('Thời gian (giây)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig(f'images/benchmark_time_informed_{cube_size}x{cube_size}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Biểu đồ số nút duyệt
    plt.figure(figsize=(10, 6))
    for name, nodes in results['informed']['nodes'].items():
        plt.plot(depths, nodes[1:], 'o-', label=name, linewidth=2)
    
    plt.title(f'Số nút duyệt của các thuật toán Informed Search (Rubik {cube_size}x{cube_size})', fontsize=14)
    plt.xlabel('Độ sâu xáo trộn', fontsize=12)
    plt.ylabel('Số nút duyệt', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig(f'images/benchmark_nodes_informed_{cube_size}x{cube_size}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Biểu đồ tỉ lệ thành công
    plt.figure(figsize=(10, 6))
    for name, success_rates in results['informed']['success'].items():
        plt.plot(depths, success_rates[1:], 'o-', label=name, linewidth=2)
    
    plt.title(f'Tỉ lệ thành công của các thuật toán Informed Search (Rubik {cube_size}x{cube_size})', fontsize=14)
    plt.xlabel('Độ sâu xáo trộn', fontsize=12)
    plt.ylabel('Tỉ lệ thành công', fontsize=12)
    plt.ylim(0, 1.05)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig(f'images/benchmark_success_informed_{cube_size}x{cube_size}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Đã lưu tất cả biểu đồ của Rubik {cube_size}x{cube_size} vào thư mục 'images/'")

if __name__ == "__main__":
    MAX_DEPTH = 7
    TIME_LIMIT = 20  # seconds
    NUM_TRIALS = 3
    
    try:
        # Chạy benchmark cho Rubik 2x2
        results_2x2 = run_benchmark(cube_size=2, max_depth=MAX_DEPTH, time_limit=TIME_LIMIT, num_trials=NUM_TRIALS)
        plot_results(results_2x2, cube_size=2, max_depth=MAX_DEPTH)
        
        # Chạy benchmark cho Rubik 3x3
        results_3x3 = run_benchmark(cube_size=3, max_depth=MAX_DEPTH, time_limit=TIME_LIMIT, num_trials=NUM_TRIALS)
        plot_results(results_3x3, cube_size=3, max_depth=MAX_DEPTH)
        
        print("Benchmark hoàn tất! Tất cả biểu đồ đã được lưu vào thư mục 'images/'")
    except KeyboardInterrupt:
        print("\nĐã hủy benchmark bởi người dùng.")
    except Exception as e:
        print(f"\nLỗi khi chạy benchmark: {e}") 