"""
Rubik's Cube 2x2 Solver Module

This module provides implementations of various search algorithms
specifically optimized for solving the 2x2 Rubik's cube.
"""

import time
import random
import heapq
import os
import pickle
from collections import deque
import math

# Import 2x2 specific classes and constants
from RubikState.rubik_2x2 import Rubik2x2State, SOLVED_STATE_2x2, MOVES_2x2, heuristic_2x2

def a_star_search_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, return_stats=False):
    """
    A* search algorithm for 2x2 Rubik's cube
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    # Get list of move names
    move_names = list(moves_dict.keys())
    
    # Count visited nodes
    nodes_visited = 0
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': 0,              # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,           # Tổng số trạng thái được tạo ra
            'pruned_nodes': 0,              # Số nút bị cắt tỉa (không thêm vào frontier)
            'max_queue_size': 0,            # Kích thước tối đa của hàng đợi ưu tiên
            'heuristic_calls': 0,           # Số lần gọi hàm heuristic
            'depth_stats': {},              # Thống kê theo độ sâu
            'heuristic_stats': {            # Thống kê về heuristic
                'min': float('inf'),
                'max': 0,
                'sum': 0,
                'avg': 0,
                'h_exact_count': 0          # Số lần h(n) = h*(n) chính xác
            },
            'effective_branching': 0.0,     # Hệ số phân nhánh hiệu quả
            'pruning_ratio': 0.0            # Tỷ lệ cắt tỉa
        }
    
    # Priority queue for A*: (f_value, state_hash, state, path)
    # Using state hash to avoid direct comparison of state objects
    h_value = heuristic_2x2(start_state)
    if return_stats:
        stats['heuristic_stats']['min'] = min(stats['heuristic_stats']['min'], h_value)
        stats['heuristic_stats']['max'] = max(stats['heuristic_stats']['max'], h_value)
        stats['heuristic_stats']['sum'] += h_value
        stats['heuristic_calls'] += 1
    
    queue = [(h_value, hash(start_state), start_state, [])]
    
    # Dictionary to track visited states and their g_values
    visited = {start_state: 0}  # state -> g_value
    
    if return_stats:
        stats['memory_used'] = 1  # start state
        stats['max_queue_size'] = 1
        stats['depth_stats'][0] = 1  # 1 node at depth 0

    start_time = time.time()
    while queue and time.time() - start_time < time_limit:
        if return_stats and len(queue) > stats['max_queue_size']:
            stats['max_queue_size'] = len(queue)
            
        f_value, _, state, path = heapq.heappop(queue)
        g_value = len(path)
        
        if state == goal_state:
            end_time = time.time()
            if return_stats:
                # Tính hệ số phân nhánh hiệu quả
                if nodes_visited > 0:
                    stats['effective_branching'] = stats['total_generated'] / nodes_visited
                
                # Tính tỷ lệ cắt tỉa
                if stats['total_generated'] > 0:
                    stats['pruning_ratio'] = (stats['pruned_nodes'] / stats['total_generated']) * 100
                
                # Tính trung bình heuristic
                if stats['heuristic_calls'] > 0:
                    stats['heuristic_stats']['avg'] = stats['heuristic_stats']['sum'] / stats['heuristic_calls']
                
                # Cập nhật số lượng trạng thái trong bộ nhớ
                stats['memory_used'] = len(visited)
                
                return path, nodes_visited, end_time - start_time, stats
            return path, nodes_visited, end_time - start_time
        
        # If we already found a better path to this state, skip it
        if g_value > visited.get(state, float('inf')):
            continue

        for move in move_names:
            nodes_visited += 1
            new_state = state.apply_move(move, moves_dict)
            new_g_value = g_value + 1
            
            if return_stats:
                stats['total_generated'] += 1
                depth = new_g_value
                stats['depth_stats'][depth] = stats['depth_stats'].get(depth, 0) + 1
            
            # Skip if we've seen this state with a shorter or equal path
            if new_state in visited and visited[new_state] <= new_g_value:
                if return_stats:
                    stats['pruned_nodes'] += 1
                continue
            
            # Update visited and add to frontier
            visited[new_state] = new_g_value
            h_score = heuristic_2x2(new_state)
            f_score = new_g_value + h_score
            
            if return_stats:
                stats['heuristic_stats']['min'] = min(stats['heuristic_stats']['min'], h_score)
                stats['heuristic_stats']['max'] = max(stats['heuristic_stats']['max'], h_score)
                stats['heuristic_stats']['sum'] += h_score
                stats['heuristic_calls'] += 1
                
                # Đánh giá độ chính xác của heuristic (tính toán đơn giản)
                if new_state == goal_state and h_score == 0:
                    stats['heuristic_stats']['h_exact_count'] += 1
            
            heapq.heappush(queue, (f_score, hash(new_state), new_state, path + [move]))

    end_time = time.time()
    if return_stats:
        # Tính hệ số phân nhánh hiệu quả
        if nodes_visited > 0:
            stats['effective_branching'] = stats['total_generated'] / nodes_visited
        
        # Tính tỷ lệ cắt tỉa
        if stats['total_generated'] > 0:
            stats['pruning_ratio'] = (stats['pruned_nodes'] / stats['total_generated']) * 100
        
        # Tính trung bình heuristic
        if stats['heuristic_calls'] > 0:
            stats['heuristic_stats']['avg'] = stats['heuristic_stats']['sum'] / stats['heuristic_calls']
        
        # Cập nhật số lượng trạng thái trong bộ nhớ
        stats['memory_used'] = len(visited)
        
        # Tính toán độ chính xác của heuristic
        if stats['heuristic_calls'] > 0:
            heuristic_accuracy = (stats['heuristic_stats']['h_exact_count'] / stats['heuristic_calls']) * 100
            stats['heuristic_accuracy'] = heuristic_accuracy
        
        return None, nodes_visited, end_time - start_time, stats
    
    return None, nodes_visited, end_time - start_time

def bfs_search_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, return_stats=False):
    """
    BFS algorithm for 2x2 Rubik's cube
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    # Get list of move names
    move_names = list(moves_dict.keys())
    
    # Count visited nodes
    nodes_visited = 0
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': 0,              # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,           # Tổng số trạng thái được tạo ra
            'pruned_nodes': 0,              # Số nút bị cắt tỉa (không thêm vào frontier)
            'max_queue_size': 0,            # Kích thước tối đa của hàng đợi
            'depth_stats': {},              # Thống kê theo độ sâu
            'effective_branching': 0.0,     # Hệ số phân nhánh hiệu quả
            'pruning_ratio': 0.0            # Tỷ lệ cắt tỉa
        }
    
    queue = deque([(start_state, [])])  # (state, path)
    visited = {start_state}
    
    if return_stats:
        stats['memory_used'] = 1  # start state in visited
        stats['max_queue_size'] = 1
        stats['depth_stats'][0] = 1  # 1 node at depth 0
    
    start_time = time.time()
    while queue and time.time() - start_time < time_limit:
        if return_stats and len(queue) > stats['max_queue_size']:
            stats['max_queue_size'] = len(queue)
            
        state, path = queue.popleft()
        nodes_visited += 1
        
        if state == goal_state:
            end_time = time.time()
            if return_stats:
                # Tính hệ số phân nhánh hiệu quả
                if nodes_visited > 0:
                    stats['effective_branching'] = stats['total_generated'] / nodes_visited
                
                # Tính tỷ lệ cắt tỉa
                if stats['total_generated'] > 0:
                    stats['pruning_ratio'] = (stats['pruned_nodes'] / stats['total_generated']) * 100
                
                # Cập nhật số lượng trạng thái trong bộ nhớ
                stats['memory_used'] = len(visited)
                
                return path, nodes_visited, end_time - start_time, stats
            return path, nodes_visited, end_time - start_time
        
        for move in move_names:
            new_state = state.apply_move(move, moves_dict)
            
            if return_stats:
                stats['total_generated'] += 1
                depth = len(path) + 1
                stats['depth_stats'][depth] = stats['depth_stats'].get(depth, 0) + 1
            
            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, path + [move]))
            elif return_stats:
                stats['pruned_nodes'] += 1
    
    end_time = time.time()
    if return_stats:
        # Tính hệ số phân nhánh hiệu quả
        if nodes_visited > 0:
            stats['effective_branching'] = stats['total_generated'] / nodes_visited
        
        # Tính tỷ lệ cắt tỉa
        if stats['total_generated'] > 0:
            stats['pruning_ratio'] = (stats['pruned_nodes'] / stats['total_generated']) * 100
        
        # Cập nhật số lượng trạng thái trong bộ nhớ
        stats['memory_used'] = len(visited)
        
        return None, nodes_visited, end_time - start_time, stats
    
    return None, nodes_visited, end_time - start_time

def dfs_search_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, max_depth=20, return_stats=False):
    """
    DFS algorithm for 2x2 Rubik's cube
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        max_depth: Maximum search depth (default is 20)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    start_time = time.time()
    visited = set()
    node_count = 0
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': 0,              # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,           # Tổng số trạng thái được tạo ra
            'pruned_nodes': 0,              # Số nút bị cắt tỉa (không thêm vào frontier)
            'max_stack_size': 0,            # Kích thước tối đa của ngăn xếp
            'depth_stats': {},              # Thống kê theo độ sâu
            'effective_branching': 0.0,     # Hệ số phân nhánh hiệu quả
            'pruning_ratio': 0.0,           # Tỷ lệ cắt tỉa
            'backtrack_count': 0            # Số lần quay lui
        }
        # Khởi tạo depth_stats cho độ sâu 0
        stats['depth_stats'][0] = 1
    
    def dfs_recursive(state, path, depth):
        nonlocal node_count
        
        if time.time() - start_time > time_limit:
            return None
        
        node_count += 1
        
        if return_stats:
            # Cập nhật thống kê theo độ sâu
            stats['depth_stats'][depth] = stats['depth_stats'].get(depth, 0) + 1
            
            # Cập nhật kích thước tối đa của ngăn xếp
            current_stack_size = len(visited)
            if current_stack_size > stats['max_stack_size']:
                stats['max_stack_size'] = current_stack_size
        
        if state == goal_state:
            return path
        
        if depth >= max_depth:
            return None
        
        for move in moves_dict:
            new_state = state.apply_move(move, moves_dict)
            
            if return_stats:
                stats['total_generated'] += 1
            
            if new_state not in visited:
                visited.add(new_state)
                result = dfs_recursive(new_state, path + [move], depth + 1)
                if result:
                    return result
                visited.remove(new_state)  # Backtrack
                
                if return_stats:
                    stats['backtrack_count'] += 1
            elif return_stats:
                stats['pruned_nodes'] += 1
        
        return None
    
    visited.add(start_state)
    result = dfs_recursive(start_state, [], 0)
    end_time = time.time()
    
    if return_stats:
        # Cập nhật số lượng trạng thái trong bộ nhớ
        stats['memory_used'] = len(visited)
        
        # Tính hệ số phân nhánh hiệu quả
        if node_count > 0:
            stats['effective_branching'] = stats['total_generated'] / node_count
        
        # Tính tỷ lệ cắt tỉa
        if stats['total_generated'] > 0:
            stats['pruning_ratio'] = (stats['pruned_nodes'] / stats['total_generated']) * 100
        
        return result, node_count, end_time - start_time, stats
    
    return result, node_count, time.time() - start_time

def ucs_search_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, return_stats=False):
    """
    Uniform Cost Search algorithm for 2x2 Rubik's cube
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    # Count time
    start_time = time.time()
    nodes_visited = 0
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': 0,              # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,           # Tổng số trạng thái được tạo ra
            'pruned_nodes': 0,              # Số nút bị cắt tỉa (không thêm vào frontier)
            'max_queue_size': 0,            # Kích thước tối đa của hàng đợi ưu tiên
            'depth_stats': {},              # Thống kê theo độ sâu
            'effective_branching': 0.0,     # Hệ số phân nhánh hiệu quả
            'pruning_ratio': 0.0            # Tỷ lệ cắt tỉa
        }
    
    # Create priority queue with (cost, hash of state, state, path)
    queue = [(0, hash(start_state), start_state, [])]
    
    # Dictionary to track visited states and their lowest costs
    visited = {start_state: 0}  # state -> cost
    
    if return_stats:
        stats['memory_used'] = 1  # start state in visited
        stats['max_queue_size'] = 1
        stats['depth_stats'][0] = 1  # 1 node at depth 0
    
    while queue and time.time() - start_time < time_limit:
        if return_stats and len(queue) > stats['max_queue_size']:
            stats['max_queue_size'] = len(queue)
            
        cost, _, state, path = heapq.heappop(queue)
        nodes_visited += 1
        
        # If current state has higher cost than the best known state, skip
        if cost > visited.get(state, float('inf')):
            continue
            
        if state == goal_state:
            end_time = time.time()
            if return_stats:
                # Tính hệ số phân nhánh hiệu quả
                if nodes_visited > 0:
                    stats['effective_branching'] = stats['total_generated'] / nodes_visited
                
                # Tính tỷ lệ cắt tỉa
                if stats['total_generated'] > 0:
                    stats['pruning_ratio'] = (stats['pruned_nodes'] / stats['total_generated']) * 100
                
                # Cập nhật số lượng trạng thái trong bộ nhớ
                stats['memory_used'] = len(visited)
                
                return path, nodes_visited, end_time - start_time, stats
            return path, nodes_visited, time.time() - start_time
            
        for move in moves_dict:
            new_state = state.apply_move(move, moves_dict)
            new_cost = cost + 1
            
            if return_stats:
                stats['total_generated'] += 1
                depth = len(path) + 1
                stats['depth_stats'][depth] = stats['depth_stats'].get(depth, 0) + 1
            
            # Only update if not visited or found a shorter path
            if new_state not in visited or new_cost < visited[new_state]:
                visited[new_state] = new_cost
                heapq.heappush(queue, (new_cost, hash(new_state), new_state, path + [move]))
            elif return_stats:
                stats['pruned_nodes'] += 1
    
    end_time = time.time()
    if return_stats:
        # Tính hệ số phân nhánh hiệu quả
        if nodes_visited > 0:
            stats['effective_branching'] = stats['total_generated'] / nodes_visited
        
        # Tính tỷ lệ cắt tỉa
        if stats['total_generated'] > 0:
            stats['pruning_ratio'] = (stats['pruned_nodes'] / stats['total_generated']) * 100
        
        # Cập nhật số lượng trạng thái trong bộ nhớ
        stats['memory_used'] = len(visited)
        
        return None, nodes_visited, end_time - start_time, stats
    
    return None, nodes_visited, end_time - start_time

def greedy_best_first_search_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, return_stats=False):
    """
    Greedy Best-First Search algorithm for 2x2 Rubik's cube
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    start_time = time.time()
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': 0,               # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,           # Tổng số trạng thái được tạo ra
            'pruned_nodes': 0,              # Số nút bị cắt tỉa
            'depth_stats': {},              # Thống kê theo độ sâu
            'effective_branching': 0.0,     # Hệ số phân nhánh hiệu quả
            'pruning_ratio': 0.0,           # Tỷ lệ cắt tỉa
            'max_depth_reached': 0,         # Độ sâu tối đa đã duyệt đến
            'max_queue_size': 0             # Kích thước hàng đợi tối đa
        }
    
    # Create priority queue with (heuristic, hash of state, state, path)
    h = heuristic_2x2(start_state)
    queue = [(h, hash(start_state), start_state, [])]
    
    visited = set([start_state])
    node_count = 0
    
    if return_stats:
        stats['memory_used'] = 1
        stats['total_generated'] = 1
        stats['max_queue_size'] = 1
    
    while queue and time.time() - start_time < time_limit:
        _, _, state, path = heapq.heappop(queue)
        node_count += 1
        
        path_length = len(path)
        
        if return_stats:
            # Cập nhật thống kê theo độ sâu
            stats['depth_stats'][path_length] = stats['depth_stats'].get(path_length, 0) + 1
            
            # Cập nhật độ sâu tối đa
            if path_length > stats['max_depth_reached']:
                stats['max_depth_reached'] = path_length
        
        if state == goal_state:
            end_time = time.time()
            
            if return_stats:
                # Tính hệ số phân nhánh hiệu quả
                if node_count > 0:
                    stats['effective_branching'] = stats['total_generated'] / node_count
                
                # Tính tỷ lệ cắt tỉa
                if stats['total_generated'] > 0:
                    stats['pruning_ratio'] = (stats['pruned_nodes'] / stats['total_generated']) * 100
                
                return path, node_count, end_time - start_time, stats
            
            return path, node_count, end_time - start_time
        
        for move in moves_dict:
            new_state = state.apply_move(move, moves_dict)
            
            if return_stats:
                stats['total_generated'] += 1
            
            if new_state not in visited:
                visited.add(new_state)
                h = heuristic_2x2(new_state)
                heapq.heappush(queue, (h, hash(new_state), new_state, path + [move]))
                
                if return_stats:
                    stats['memory_used'] += 1
                    if len(queue) > stats['max_queue_size']:
                        stats['max_queue_size'] = len(queue)
            elif return_stats:
                stats['pruned_nodes'] += 1
    
    end_time = time.time()
    
    if return_stats:
        # Tính hệ số phân nhánh hiệu quả
        if node_count > 0:
            stats['effective_branching'] = stats['total_generated'] / node_count
        
        # Tính tỷ lệ cắt tỉa
        if stats['total_generated'] > 0:
            stats['pruning_ratio'] = (stats['pruned_nodes'] / stats['total_generated']) * 100
        
        return None, node_count, end_time - start_time, stats
    
    return None, node_count, end_time - start_time

def ids_search_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, max_depth=20, return_stats=False):
    """
    Iterative Deepening Search algorithm for 2x2 Rubik's cube
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        max_depth: Maximum search depth (default is 20)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    start_time = time.time()
    node_count = 0
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': 0,               # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,           # Tổng số trạng thái được tạo ra
            'pruned_nodes': 0,              # Số nút bị cắt tỉa
            'depth_stats': {},              # Thống kê theo độ sâu
            'iterations': 0,                # Số lần lặp (tăng độ sâu)
            'effective_branching': 0.0,     # Hệ số phân nhánh hiệu quả
            'pruning_ratio': 0.0,           # Tỷ lệ cắt tỉa
            'max_depth_reached': 0          # Độ sâu tối đa đã duyệt đến
        }
    
    for depth in range(1, max_depth + 1):
        if return_stats:
            stats['iterations'] += 1
            
        visited = set()
        visited.add(start_state)
        
        if return_stats:
            max_memory_size = 1
        
        def dls(state, path, current_depth):
            nonlocal node_count
            
            if time.time() - start_time > time_limit:
                return None
            
            node_count += 1
            
            if return_stats:
                # Cập nhật thống kê theo độ sâu
                stats['depth_stats'][current_depth] = stats['depth_stats'].get(current_depth, 0) + 1
                
                # Cập nhật độ sâu tối đa
                if current_depth > stats['max_depth_reached']:
                    stats['max_depth_reached'] = current_depth
            
            if state == goal_state:
                return path
            
            if current_depth == depth:
                return None
            
            for move in moves_dict:
                new_state = state.apply_move(move, moves_dict)
                
                if return_stats:
                    stats['total_generated'] += 1
                
                if new_state not in visited:
                    visited.add(new_state)
                    
                    if return_stats:
                        nonlocal max_memory_size
                        if len(visited) > max_memory_size:
                            max_memory_size = len(visited)
                    
                    result = dls(new_state, path + [move], current_depth + 1)
                    if result:
                        return result
                    visited.remove(new_state)  # Backtrack
                elif return_stats:
                    stats['pruned_nodes'] += 1
            
            return None
        
        # Khởi tạo max_memory_size nếu đang thu thập thống kê
        if return_stats:
            max_memory_size = 1
        
        result = dls(start_state, [], 0)
        
        if return_stats and max_memory_size > stats['memory_used']:
            stats['memory_used'] = max_memory_size
        
        if result:
            end_time = time.time()
            
            if return_stats:
                # Tính hệ số phân nhánh hiệu quả
                if node_count > 0:
                    stats['effective_branching'] = stats['total_generated'] / node_count
                
                # Tính tỷ lệ cắt tỉa
                if stats['total_generated'] > 0:
                    stats['pruning_ratio'] = (stats['pruned_nodes'] / stats['total_generated']) * 100
                
                return result, node_count, end_time - start_time, stats
            
            return result, node_count, end_time - start_time
        
        if time.time() - start_time > time_limit:
            break
    
    end_time = time.time()
    
    if return_stats:
        # Tính hệ số phân nhánh hiệu quả
        if node_count > 0:
            stats['effective_branching'] = stats['total_generated'] / node_count
        
        # Tính tỷ lệ cắt tỉa
        if stats['total_generated'] > 0:
            stats['pruning_ratio'] = (stats['pruned_nodes'] / stats['total_generated']) * 100
        
        return None, node_count, end_time - start_time, stats
    
    return None, node_count, end_time - start_time

def ida_star_search_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, return_stats=False):
    """
    IDA* Search algorithm for 2x2 Rubik's cube
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    start_time = time.time()
    visited_nodes = 0
    threshold = heuristic_2x2(start_state)
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': 0,               # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,           # Tổng số trạng thái được tạo ra
            'pruned_nodes': 0,              # Số nút bị cắt tỉa
            'depth_stats': {},              # Thống kê theo độ sâu
            'iterations': 0,                # Số lần lặp (tăng threshold)
            'effective_branching': 0.0,     # Hệ số phân nhánh hiệu quả
            'pruning_ratio': 0.0,           # Tỷ lệ cắt tỉa
            'max_depth_reached': 0,         # Độ sâu tối đa đã duyệt đến
            'thresholds': [threshold],      # Các ngưỡng f đã sử dụng
            'heuristic_stats': {            # Thống kê về heuristic
                'min': float('inf'),
                'max': 0,
                'sum': 0,
                'avg': 0,
                'calls': 0
            }
        }
        
        # Ghi nhận heuristic đầu tiên
        stats['heuristic_stats']['min'] = min(stats['heuristic_stats']['min'], threshold)
        stats['heuristic_stats']['max'] = max(stats['heuristic_stats']['max'], threshold)
        stats['heuristic_stats']['sum'] += threshold
        stats['heuristic_stats']['calls'] += 1
    
    while time.time() - start_time < time_limit:
        if return_stats:
            stats['iterations'] += 1
            
        visited = set()
        path, found, new_threshold, nodes = _dfs_with_limit_2x2(
            start_state, goal_state, [], 0, threshold, visited, 
            moves_dict, start_time, time_limit, return_stats, stats if return_stats else None
        )
        visited_nodes += nodes
        
        if found:
            end_time = time.time()
            if return_stats:
                # Cập nhật kích thước bộ nhớ tối đa
                if len(visited) > stats['memory_used']:
                    stats['memory_used'] = len(visited)
                
                # Tính hệ số phân nhánh hiệu quả
                if visited_nodes > 0:
                    stats['effective_branching'] = stats['total_generated'] / visited_nodes
                
                # Tính tỷ lệ cắt tỉa
                if stats['total_generated'] > 0:
                    stats['pruning_ratio'] = (stats['pruned_nodes'] / stats['total_generated']) * 100
                
                # Tính trung bình heuristic
                if stats['heuristic_stats']['calls'] > 0:
                    stats['heuristic_stats']['avg'] = stats['heuristic_stats']['sum'] / stats['heuristic_stats']['calls']
                    
                return path, visited_nodes, end_time - start_time, stats
            return path, visited_nodes, end_time - start_time
        
        if new_threshold == float('inf'):
            break
        
        threshold = new_threshold
        if return_stats:
            stats['thresholds'].append(threshold)
    
    end_time = time.time()
    if return_stats:
        # Tính hệ số phân nhánh hiệu quả
        if visited_nodes > 0:
            stats['effective_branching'] = stats['total_generated'] / visited_nodes
        
        # Tính tỷ lệ cắt tỉa
        if stats['total_generated'] > 0:
            stats['pruning_ratio'] = (stats['pruned_nodes'] / stats['total_generated']) * 100
        
        # Tính trung bình heuristic
        if stats['heuristic_stats']['calls'] > 0:
            stats['heuristic_stats']['avg'] = stats['heuristic_stats']['sum'] / stats['heuristic_stats']['calls']
            
        return None, visited_nodes, end_time - start_time, stats
    
    return None, visited_nodes, end_time - start_time

def _dfs_with_limit_2x2(state, goal_state, path, g, threshold, visited, moves_dict, start_time, time_limit, return_stats=False, stats=None):
    """
    Helper function for IDA* search for 2x2, performs depth-first search up to a limit
    
    Args:
        state: Current state
        goal_state: Target state
        path: Current path
        g: Current cost
        threshold: Current f-value threshold
        visited: Set of visited states
        moves_dict: Dictionary of moves
        start_time: Start time of the search
        time_limit: Time limit for the search
        return_stats: Whether to return detailed statistics
        stats: Statistics dictionary to update
    
    Returns:
        tuple: (path, found, new_threshold, nodes_visited)
    """
    if time.time() - start_time >= time_limit:
        return None, False, float('inf'), 0
    
    if state == goal_state:
        return path, True, threshold, 1
    
    visited.add(state)
    nodes_visited = 1
    
    if return_stats:
        # Cập nhật thống kê theo độ sâu
        depth = g
        stats['depth_stats'][depth] = stats['depth_stats'].get(depth, 0) + 1
        
        # Cập nhật độ sâu tối đa
        if depth > stats['max_depth_reached']:
            stats['max_depth_reached'] = depth
        
        # Cập nhật kích thước bộ nhớ
        if len(visited) > stats['memory_used']:
            stats['memory_used'] = len(visited)
    
    h = heuristic_2x2(state)
    f = g + h
    
    if return_stats:
        # Ghi nhận heuristic
        stats['heuristic_stats']['min'] = min(stats['heuristic_stats']['min'], h)
        stats['heuristic_stats']['max'] = max(stats['heuristic_stats']['max'], h)
        stats['heuristic_stats']['sum'] += h
        stats['heuristic_stats']['calls'] += 1
    
    if f > threshold:
        return None, False, f, nodes_visited
    
    min_threshold = float('inf')
    
    for move in moves_dict:
        new_state = state.apply_move(move, moves_dict)
        
        if return_stats:
            stats['total_generated'] += 1
        
        if new_state in visited:
            if return_stats:
                stats['pruned_nodes'] += 1
            continue
            
        new_path, found, new_threshold, nodes = _dfs_with_limit_2x2(
            new_state, goal_state, path + [move], g + 1, threshold, visited.copy(), 
            moves_dict, start_time, time_limit, return_stats, stats
        )
        
        nodes_visited += nodes
        
        if found:
            return new_path, True, threshold, nodes_visited
            
        if new_threshold < min_threshold:
            min_threshold = new_threshold
    
    visited.remove(state)  # Backtrack
    return None, False, min_threshold, nodes_visited

def hill_climbing_max_search_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, max_iterations=1000, return_stats=False):
    """
    Hill Climbing Max algorithm for 2x2 Rubik's cube
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        max_iterations: Maximum number of iterations (default is 1000)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    # Get list of move names
    move_names = list(moves_dict.keys())
    
    # Count visited nodes
    nodes_visited = 0
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': 1,               # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,           # Tổng số trạng thái được tạo ra
            'pruned_nodes': 0,              # Số nút bị cắt tỉa
            'depth_stats': {0: 1},          # Thống kê theo độ sâu
            'iterations': 0,                # Số lần lặp
            'max_depth_reached': 0,         # Độ sâu tối đa đã duyệt đến
            'neighbors_stats': {            # Thống kê về hàng xóm
                'min': float('inf'),
                'max': 0,
                'avg': 0,
                'count': 0
            }
        }
    
    current_state = start_state
    current_h = heuristic_2x2(current_state)
    path = []
    
    start_time = time.time()
    
    # Iterate until goal is reached or no further improvement
    for iteration in range(max_iterations):
        if return_stats:
            stats['iterations'] += 1
            current_depth = len(path)
            if current_depth > stats['max_depth_reached']:
                stats['max_depth_reached'] = current_depth
        
        if time.time() - start_time > time_limit:  # Check time limit first
            if return_stats:
                return None, nodes_visited, time.time() - start_time, stats
            return None, nodes_visited, time.time() - start_time
            
        if current_state == goal_state:
            end_time = time.time()
            if return_stats:
                return path, nodes_visited, end_time - start_time, stats
            return path, nodes_visited, end_time - start_time
        
        # Find the best neighbor
        best_neighbor = None
        best_move = None
        best_h = current_h
        
        neighbors_examined = 0
        
        for move in move_names:
            nodes_visited += 1
            neighbor = current_state.apply_move(move, moves_dict)
            neighbor_h = heuristic_2x2(neighbor)
            
            if return_stats:
                stats['total_generated'] += 1
                neighbors_examined += 1
                
                # Update neighbor heuristic stats
                if neighbor_h < stats['neighbors_stats']['min']:
                    stats['neighbors_stats']['min'] = neighbor_h
                if neighbor_h > stats['neighbors_stats']['max']:
                    stats['neighbors_stats']['max'] = neighbor_h
                stats['neighbors_stats']['count'] += 1
                stats['neighbors_stats']['avg'] = ((stats['neighbors_stats']['avg'] * 
                    (stats['neighbors_stats']['count'] - 1)) + neighbor_h) / stats['neighbors_stats']['count']
            
            # Find neighbor with lowest heuristic (best)
            if neighbor_h < best_h:
                best_neighbor = neighbor
                best_move = move
                best_h = neighbor_h
        
        # If no improvement, end
        if best_neighbor is None:
            break
        
        # Move to the best state
        current_state = best_neighbor
        current_h = best_h
        path.append(best_move)
        
        if return_stats:
            depth = len(path)
            stats['depth_stats'][depth] = stats['depth_stats'].get(depth, 0) + 1
            stats['memory_used'] += 1
    
    # If goal is reached, return path
    if current_state == goal_state:
        end_time = time.time()
        if return_stats:
            return path, nodes_visited, end_time - start_time, stats
        return path, nodes_visited, end_time - start_time
    
    # No path found
    if return_stats:
        return None, nodes_visited, time.time() - start_time, stats
    return None, nodes_visited, time.time() - start_time

def hill_climbing_random_search_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, max_iterations=1000, return_stats=False):
    """
    Hill Climbing Random algorithm for 2x2 Rubik's cube
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        max_iterations: Maximum number of iterations (default is 1000)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    # Get list of move names
    move_names = list(moves_dict.keys())
    
    # Count visited nodes
    nodes_visited = 0
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': 1,               # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,           # Tổng số trạng thái được tạo ra
            'pruned_nodes': 0,              # Số nút bị cắt tỉa
            'depth_stats': {0: 1},          # Thống kê theo độ sâu
            'iterations': 0,                # Số lần lặp
            'max_depth_reached': 0,         # Độ sâu tối đa đã duyệt đến
            'better_neighbors_count': [],   # Số lượng hàng xóm tốt hơn qua các lần lặp
            'neighbors_stats': {            # Thống kê về hàng xóm
                'min': float('inf'),
                'max': 0,
                'avg': 0,
                'count': 0
            }
        }
    
    current_state = start_state
    current_h = heuristic_2x2(current_state)
    path = []
    
    start_time = time.time()
    
    # Iterate until goal is reached or no further improvement
    for iteration in range(max_iterations):
        if return_stats:
            stats['iterations'] += 1
            current_depth = len(path)
            if current_depth > stats['max_depth_reached']:
                stats['max_depth_reached'] = current_depth
        
        if time.time() - start_time > time_limit:  # Check time limit first
            if return_stats:
                return None, nodes_visited, time.time() - start_time, stats
            return None, nodes_visited, time.time() - start_time
            
        if current_state == goal_state:
            end_time = time.time()
            if return_stats:
                return path, nodes_visited, end_time - start_time, stats
            return path, nodes_visited, end_time - start_time
        
        # Find all better neighbors
        better_neighbors = []
        
        for move in move_names:
            nodes_visited += 1
            neighbor = current_state.apply_move(move, moves_dict)
            neighbor_h = heuristic_2x2(neighbor)
            
            if return_stats:
                stats['total_generated'] += 1
                
                # Update neighbor heuristic stats
                if neighbor_h < stats['neighbors_stats']['min']:
                    stats['neighbors_stats']['min'] = neighbor_h
                if neighbor_h > stats['neighbors_stats']['max']:
                    stats['neighbors_stats']['max'] = neighbor_h
                stats['neighbors_stats']['count'] += 1
                stats['neighbors_stats']['avg'] = ((stats['neighbors_stats']['avg'] * 
                    (stats['neighbors_stats']['count'] - 1)) + neighbor_h) / stats['neighbors_stats']['count']
            
            # Find neighbors with better heuristic
            if neighbor_h < current_h:
                better_neighbors.append((neighbor, move, neighbor_h))
        
        if return_stats:
            stats['better_neighbors_count'].append(len(better_neighbors))
        
        # If no improvement, end
        if not better_neighbors:
            break
        
        # Randomly choose a better neighbor
        chosen = random.choice(better_neighbors)
        current_state, best_move, current_h = chosen
        path.append(best_move)
        
        if return_stats:
            depth = len(path)
            stats['depth_stats'][depth] = stats['depth_stats'].get(depth, 0) + 1
            stats['memory_used'] += 1
    
    # If goal is reached, return path
    if current_state == goal_state:
        end_time = time.time()
        if return_stats:
            return path, nodes_visited, end_time - start_time, stats
        return path, nodes_visited, end_time - start_time
    
    # No path found
    if return_stats:
        return None, nodes_visited, time.time() - start_time, stats
    return None, nodes_visited, time.time() - start_time

def pdb_heuristic_2x2(state, pdb):
    """
    Heuristic function using the pattern database for 2x2 Rubik's cube
    
    Args:
        state: Current state (Rubik2x2State)
        pdb: Pattern database
        
    Returns:
        int: Heuristic value
    """
    cp_value = pdb.cp_database.get(tuple(state.cp), 0)
    co_value = pdb.co_database.get(tuple(state.co), 0)
    
    # Return the maximum since both subproblems must be solved
    return max(cp_value, co_value)

def a_star_pdb_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, pdb=None, return_stats=False):
    """
    A* algorithm for 2x2 Rubik's Cube using Pattern Database heuristic
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        pdb: Pattern database
        return_stats: Whether to return detailed statistics (default is False)
        
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    if pdb is None:
        raise ValueError("Pattern database is required for A* PDB algorithm")
    
    start_time = time.time()
    nodes_explored = 0
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': 0,               # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,           # Tổng số trạng thái được tạo ra
            'pruned_nodes': 0,              # Số nút bị cắt tỉa
            'depth_stats': {},              # Thống kê theo độ sâu
            'effective_branching': 0.0,     # Hệ số phân nhánh hiệu quả
            'pruning_ratio': 0.0,           # Tỷ lệ cắt tỉa
            'max_depth_reached': 0,         # Độ sâu tối đa đã duyệt đến
            'max_queue_size': 0,            # Kích thước hàng đợi tối đa
            'heuristic_stats': {            # Thống kê về heuristic
                'min': float('inf'),
                'max': 0,
                'sum': 0,
                'avg': 0,
                'calls': 0
            }
        }
    
    # Priority queue for A*: (f_value, state_hash, state, path)
    # f_value = g_value (path length) + h_value (heuristic)
    h_value = pdb_heuristic_2x2(start_state, pdb)
    frontier = [(h_value, hash(start_state), start_state, [])]
    
    # Dictionary to track visited states and their shortest paths
    visited = {start_state: 0}  # state -> g_value
    
    if return_stats:
        stats['memory_used'] = 1  # start state
        stats['total_generated'] = 1
        stats['max_queue_size'] = 1
        stats['depth_stats'][0] = 1  # 1 node at depth 0
        
        # Ghi nhận heuristic đầu tiên
        stats['heuristic_stats']['min'] = min(stats['heuristic_stats']['min'], h_value)
        stats['heuristic_stats']['max'] = max(stats['heuristic_stats']['max'], h_value)
        stats['heuristic_stats']['sum'] += h_value
        stats['heuristic_stats']['calls'] += 1
    
    while frontier and time.time() - start_time < time_limit:
        if return_stats and len(frontier) > stats['max_queue_size']:
            stats['max_queue_size'] = len(frontier)
            
        f_value, _, state, path = heapq.heappop(frontier)
        nodes_explored += 1
        
        g_value = len(path)
        
        if return_stats:
            if g_value > stats['max_depth_reached']:
                stats['max_depth_reached'] = g_value
            
            # Cập nhật thống kê theo độ sâu
            stats['depth_stats'][g_value] = stats['depth_stats'].get(g_value, 0) + 1
        
        # Check if we reached the goal
        if state == goal_state:
            end_time = time.time()
            
            if return_stats:
                # Tính hệ số phân nhánh hiệu quả
                if nodes_explored > 0:
                    stats['effective_branching'] = stats['total_generated'] / nodes_explored
                
                # Tính tỷ lệ cắt tỉa
                if stats['total_generated'] > 0:
                    stats['pruning_ratio'] = (stats['pruned_nodes'] / stats['total_generated']) * 100
                
                return path, nodes_explored, end_time - start_time, stats
            
            return path, nodes_explored, end_time - start_time
        
        # If we already found a better path to this state, skip it
        if g_value > visited.get(state, float('inf')):
            continue
        
        # Try all possible moves
        for move in moves_dict:
            new_state = state.apply_move(move, moves_dict)
            new_g_value = g_value + 1
            
            if return_stats:
                stats['total_generated'] += 1
            
            # Skip if we've seen this state with a shorter or equal path
            if new_state in visited and visited[new_state] <= new_g_value:
                if return_stats:
                    stats['pruned_nodes'] += 1
                continue
            
            # Update visited and add to frontier
            visited[new_state] = new_g_value
            h_value = pdb_heuristic_2x2(new_state, pdb)
            
            if return_stats:
                stats['memory_used'] += 1
                
                # Ghi nhận heuristic
                stats['heuristic_stats']['min'] = min(stats['heuristic_stats']['min'], h_value)
                stats['heuristic_stats']['max'] = max(stats['heuristic_stats']['max'], h_value)
                stats['heuristic_stats']['sum'] += h_value
                stats['heuristic_stats']['calls'] += 1
            
            heapq.heappush(frontier, (new_g_value + h_value, hash(new_state), new_state, path + [move]))
    
    end_time = time.time()
    
    if return_stats:
        # Tính hệ số phân nhánh hiệu quả
        if nodes_explored > 0:
            stats['effective_branching'] = stats['total_generated'] / nodes_explored
        
        # Tính tỷ lệ cắt tỉa
        if stats['total_generated'] > 0:
            stats['pruning_ratio'] = (stats['pruned_nodes'] / stats['total_generated']) * 100
        
        # Tính trung bình heuristic
        if stats['heuristic_stats']['calls'] > 0:
            stats['heuristic_stats']['avg'] = stats['heuristic_stats']['sum'] / stats['heuristic_stats']['calls']
        
        return None, nodes_explored, end_time - start_time, stats
    
    return None, nodes_explored, end_time - start_time

def load_pattern_database(file_path=None):
    """
    Load the pattern database for 2x2 Rubik's cube from a file
    
    Args:
        file_path: Path to the pattern database file
        
    Returns:
        PatternDatabase or None if not found
    """
    try:
        from pdb_rubik_2x2 import PatternDatabase
        
        # Try multiple possible paths if not specified
        if file_path is None:
            possible_paths = [
                "rubik_2x2_pdb.pkl",  # Current directory
                os.path.join(os.path.dirname(__file__), "..", "rubik_2x2_pdb.pkl"),  # One level up
                os.path.abspath("rubik_2x2_pdb.pkl"),  # Absolute path
                os.path.join(os.getcwd(), "rubik_2x2_pdb.pkl")  # Current working directory
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    print(f"Found PDB file at: {path}")
                    pdb = PatternDatabase(path)
                    if pdb.load():
                        print(f"Successfully loaded PDB: CP={len(pdb.cp_database)} entries, CO={len(pdb.co_database)} entries")
                        return pdb
        else:
            # Use specified path
            if os.path.exists(file_path):
                pdb = PatternDatabase(file_path)
                if pdb.load():
                    print(f"Successfully loaded PDB from {file_path}")
                    return pdb
        
        print("Pattern database not found or failed to load")
        return None
        
    except ImportError as e:
        print(f"Pattern Database module not available: {e}")
        return None
    except Exception as e:
        print(f"Error loading Pattern Database: {e}")
        return None

def solve_2x2(start_state, algorithm="a_star", time_limit=30, return_stats=False):
    """
    Solve 2x2 Rubik's cube using specified algorithm
    
    Args:
        start_state: Starting state (Rubik2x2State)
        algorithm: Name of algorithm to use
        time_limit: Time limit in seconds
        return_stats: Whether to return detailed statistics
        
    Returns:
        tuple: (solution_path, nodes_visited, time_taken) or (solution_path, nodes_visited, time_taken, stats)
    """
    algorithm_funcs = {
        "a_star": a_star_search_2x2,
        "bfs": bfs_search_2x2,
        "dfs": dfs_search_2x2,
        "ucs": ucs_search_2x2,
        "greedy_best_first": greedy_best_first_search_2x2,
        "ida_star": ida_star_search_2x2,
        "ids": ids_search_2x2,
        "hill_climbing_max": hill_climbing_max_search_2x2,
        "hill_climbing_random": hill_climbing_random_search_2x2,
        "pdb_astar": lambda state, time_limit=30, return_stats=False: a_star_pdb_2x2(state, time_limit=time_limit, pdb=load_pattern_database(), return_stats=return_stats),
        # Thêm các thuật toán mới
        "simulated_annealing": simulated_annealing_search_2x2,
        "genetic_algorithm": genetic_algorithm_search_2x2,
        "local_beam_search": local_beam_search_2x2,
        "and_or_graph_search": and_or_graph_search_2x2,
        "belief_states_search": belief_states_search_2x2,
        "ac3": ac3_search_2x2,
        "backtracking_strategy1": backtracking_search_strategy1_2x2,
        "backtracking_strategy2": backtracking_search_strategy2_2x2,
    }
    
    if algorithm not in algorithm_funcs:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    func = algorithm_funcs[algorithm]
    return func(start_state, time_limit=time_limit, return_stats=return_stats)

def test_scramble_2x2(scramble_moves, algorithm="a_star", time_limit=30):
    """
    Test a specific scramble sequence on a 2x2 Rubik's cube
    
    Args:
        scramble_moves: List of move strings
        algorithm: Algorithm to use (default is "a_star")
        time_limit: Time limit in seconds (default is 30)
        
    Returns:
        bool: True if solved successfully
    """
    # Create a solved state and apply scramble
    start_state = SOLVED_STATE_2x2.copy()
    print(f"Testing scramble: {' '.join(scramble_moves)}")
    
    # Apply scramble moves
    for move in scramble_moves:
        start_state = start_state.apply_move(move, MOVES_2x2)
    
    # Solve the scrambled state
    solution, nodes, time_taken = solve_2x2(start_state, algorithm, time_limit)
    
    # Check if solved
    if solution:
        print(f"Solution found: {' '.join(solution)}")
        print(f"Solution length: {len(solution)}")
        print(f"Nodes explored: {nodes}")
        print(f"Time taken: {time_taken:.2f} seconds")
        
        # Verify solution
        test_state = start_state.copy()
        for move in solution:
            test_state = test_state.apply_move(move, MOVES_2x2)
        
        if test_state == SOLVED_STATE_2x2:
            print("✓ Solution verified")
            return True
        else:
            print("✗ Solution verification failed!")
            return False
    else:
        print(f"No solution found within {time_limit} seconds")
        print(f"Nodes explored: {nodes}")
        return False

def simulated_annealing_search_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, max_iterations=1000, initial_temp=100, cooling_rate=0.95, return_stats=False):
    """
    Simulated Annealing search algorithm for 2x2 Rubik's cube
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        max_iterations: Maximum number of iterations (default is 1000)
        initial_temp: Initial temperature (default is 100)
        cooling_rate: Rate at which temperature decreases (default is 0.95)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    # Get list of move names
    move_names = list(moves_dict.keys())
    
    # Count visited nodes
    nodes_visited = 0
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': 1,              # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,           # Tổng số trạng thái được tạo ra
            'accepted_worse': 0,            # Số lần chấp nhận trạng thái tệ hơn
            'temperature_curve': [],        # Đường cong nhiệt độ
            'best_h_values': [],            # Giá trị heuristic tốt nhất theo thời gian
            'current_h_values': [],         # Giá trị heuristic hiện tại theo thời gian
        }

    # TODO: Implement Simulated Annealing algorithm
    # Current implementation is just a placeholder

    start_time = time.time()
    current_state = start_state
    current_path = []
    current_h = heuristic_2x2(current_state)
    best_state = current_state
    best_path = current_path
    best_h = current_h
    
    temperature = initial_temp
    iteration = 0
    
    while time.time() - start_time < time_limit and iteration < max_iterations and best_h > 0:
        # Choose a random move
        move = random.choice(move_names)
        new_state = current_state.apply_move(move, moves_dict)
        nodes_visited += 1
        new_h = heuristic_2x2(new_state)
        
        if return_stats:
            stats['total_generated'] += 1
        
        # Calculate energy/cost change
        delta_h = new_h - current_h
        
        # Accept if better, or with some probability if worse
        if delta_h <= 0 or random.random() < math.exp(-delta_h / temperature):
            current_state = new_state
            current_path.append(move)
            current_h = new_h
            
            if return_stats and delta_h > 0:
                stats['accepted_worse'] += 1
        
        # Update best solution if found better
        if current_h < best_h:
            best_state = current_state
            best_path = list(current_path)
            best_h = current_h
        
        # Cool down
        temperature *= cooling_rate
        iteration += 1
        
        if return_stats:
            stats['temperature_curve'].append(temperature)
            stats['best_h_values'].append(best_h)
            stats['current_h_values'].append(current_h)
    
    end_time = time.time()
    
    # If we found the goal state
    if best_state == goal_state:
        if return_stats:
            return best_path, nodes_visited, end_time - start_time, stats
        return best_path, nodes_visited, end_time - start_time
    
    # No solution found
    if return_stats:
        return None, nodes_visited, end_time - start_time, stats
    return None, nodes_visited, end_time - start_time

def genetic_algorithm_search_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, population_size=100, generations=1000, mutation_rate=0.1, return_stats=False):
    """
    Genetic Algorithm search for 2x2 Rubik's cube
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        population_size: Size of the population (default is 100)
        generations: Maximum number of generations (default is 1000)
        mutation_rate: Probability of mutation (default is 0.1)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    # Get list of move names
    move_names = list(moves_dict.keys())
    
    # Count visited nodes
    nodes_visited = 0
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': population_size,    # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,              # Tổng số trạng thái được tạo ra
            'best_fitness': [],                # Độ thích nghi tốt nhất theo thế hệ
            'avg_fitness': [],                 # Độ thích nghi trung bình theo thế hệ
            'diversity': [],                   # Đa dạng quần thể theo thế hệ
        }

    # TODO: Implement Genetic Algorithm
    # Current implementation is just a placeholder
    
    start_time = time.time()
    # No solution found
    if return_stats:
        return None, nodes_visited, time.time() - start_time, stats
    return None, nodes_visited, time.time() - start_time

def local_beam_search_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, beam_width=10, max_iterations=1000, return_stats=False):
    """
    Local Beam Search algorithm for 2x2 Rubik's cube
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        beam_width: Number of states to keep track of (default is 10)
        max_iterations: Maximum number of iterations (default is 1000)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    # Get list of move names
    move_names = list(moves_dict.keys())
    
    # Count visited nodes
    nodes_visited = 0
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': beam_width,         # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,              # Tổng số trạng thái được tạo ra
            'best_h_values': [],               # Giá trị heuristic tốt nhất theo lần lặp
            'beam_diversity': [],              # Đa dạng của các trạng thái trong beam
        }

    # TODO: Implement Local Beam Search
    # Current implementation is just a placeholder
    
    start_time = time.time()
    # No solution found
    if return_stats:
        return None, nodes_visited, time.time() - start_time, stats
    return None, nodes_visited, time.time() - start_time

def and_or_graph_search_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, max_depth=10, return_stats=False):
    """
    AND-OR Graph Search algorithm for 2x2 Rubik's cube
    For complex environment search problems
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        max_depth: Maximum search depth (default is 10)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    # Get list of move names
    move_names = list(moves_dict.keys())
    
    # Count visited nodes
    nodes_visited = 0
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': 0,                  # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,              # Tổng số trạng thái được tạo ra
            'and_nodes': 0,                    # Số nút AND
            'or_nodes': 0,                     # Số nút OR
        }

    # TODO: Implement AND-OR Graph Search
    # Current implementation is just a placeholder
    
    start_time = time.time()
    # No solution found
    if return_stats:
        return None, nodes_visited, time.time() - start_time, stats
    return None, nodes_visited, time.time() - start_time

def belief_states_search_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, max_iterations=1000, return_stats=False):
    """
    Belief States Search algorithm for 2x2 Rubik's cube
    For complex environment search problems with uncertainty
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        max_iterations: Maximum number of iterations (default is 1000)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    # Get list of move names
    move_names = list(moves_dict.keys())
    
    # Count visited nodes
    nodes_visited = 0
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': 0,                  # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,              # Tổng số trạng thái được tạo ra
            'belief_state_sizes': [],          # Kích thước của các belief state
            'entropy': [],                     # Entropy của belief state theo thời gian
        }

    # TODO: Implement Belief States Search
    # Current implementation is just a placeholder
    
    start_time = time.time()
    # No solution found
    if return_stats:
        return None, nodes_visited, time.time() - start_time, stats
    return None, nodes_visited, time.time() - start_time

def ac3_search_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, return_stats=False):
    """
    AC-3 (Arc Consistency Algorithm 3) for 2x2 Rubik's cube
    Constraint Satisfaction Problem approach
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    # Get list of move names
    move_names = list(moves_dict.keys())
    
    # Count visited nodes
    nodes_visited = 0
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': 0,                  # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,              # Tổng số trạng thái được tạo ra
            'arcs_processed': 0,               # Số cung đã xử lý
            'domain_reductions': 0,            # Số lần giảm miền giá trị
        }

    # TODO: Implement AC-3 algorithm
    # Current implementation is just a placeholder
    
    start_time = time.time()
    # No solution found
    if return_stats:
        return None, nodes_visited, time.time() - start_time, stats
    return None, nodes_visited, time.time() - start_time

def backtracking_search_strategy1_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, return_stats=False):
    """
    Backtracking Search for 2x2 Rubik's cube - Strategy 1 (Variable Assignment)
    Standard CSP backtracking, assigning values to one variable at a time
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    # Get list of move names
    move_names = list(moves_dict.keys())
    
    # Count visited nodes
    nodes_visited = 0
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': 0,                  # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,              # Tổng số trạng thái được tạo ra
            'backtracks': 0,                   # Số lần quay lui
            'constraints_checked': 0,          # Số lần kiểm tra ràng buộc
        }

    # TODO: Implement Backtracking Search Strategy 1
    # Current implementation is just a placeholder
    
    start_time = time.time()
    # No solution found
    if return_stats:
        return None, nodes_visited, time.time() - start_time, stats
    return None, nodes_visited, time.time() - start_time

def backtracking_search_strategy2_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, return_stats=False):
    """
    Backtracking Search for 2x2 Rubik's cube - Strategy 2 (Early Constraint Check)
    CSP backtracking with forward checking to prune search space
    
    Args:
        start_state: Starting state (Rubik2x2State)
        goal_state: Goal state (default is SOLVED_STATE_2x2)
        moves_dict: Dictionary of moves (default is MOVES_2x2)
        time_limit: Time limit in seconds (default is 30)
        return_stats: Whether to return detailed statistics (default is False)
    
    Returns:
        tuple: (path, nodes_visited, time_taken) or (path, nodes_visited, time_taken, stats)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_2x2
    moves_dict = moves_dict or MOVES_2x2
    
    # Get list of move names
    move_names = list(moves_dict.keys())
    
    # Count visited nodes
    nodes_visited = 0
    
    # Thêm thống kê
    if return_stats:
        stats = {
            'memory_used': 0,                  # Số lượng trạng thái được lưu trong bộ nhớ
            'total_generated': 0,              # Tổng số trạng thái được tạo ra
            'backtracks': 0,                   # Số lần quay lui
            'constraints_checked': 0,          # Số lần kiểm tra ràng buộc
            'pruned_branches': 0,              # Số nhánh bị cắt tỉa
        }

    # TODO: Implement Backtracking Search Strategy 2
    # Current implementation is just a placeholder
    
    start_time = time.time()
    # No solution found
    if return_stats:
        return None, nodes_visited, time.time() - start_time, stats
    return None, nodes_visited, time.time() - start_time

if __name__ == "__main__":
    # Test the 2x2 solver with a simple scramble
    scramble = ["R", "U", "R'", "U'"]
    test_scramble_2x2(scramble) 