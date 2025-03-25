# 🧩 Rubik's Cube Solver

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Algorithm](https://img.shields.io/badge/Algorithm-A*%20%7C%20BFS-green)
![Version](https://img.shields.io/badge/version-1.0.0-orange)

## 📖 Giới thiệu | Introduction

Dự án này là một giải pháp giải khối Rubik sử dụng thuật toán A* và BFS (Breadth-First Search). Chương trình mô hình hóa khối Rubik 3x3x3 và tìm ra chuỗi các bước di chuyển tối ưu để đưa khối Rubik từ trạng thái xáo trộn về trạng thái đã được giải.

*This project is a Rubik's Cube solver using A* and BFS (Breadth-First Search) algorithms. The program models a 3x3x3 Rubik's Cube and finds the optimal sequence of moves to transform a scrambled cube to its solved state.*

## ✨ Tính năng chính | Key Features

- Biểu diễn khối Rubik 3x3x3 với đầy đủ hoán vị và định hướng các khối góc và cạnh
- Thuật toán A* với hàm đánh giá heuristic thông minh tối ưu quá trình tìm kiếm
- Thuật toán BFS để tìm ra lời giải ngắn nhất
- So sánh hiệu suất giữa các thuật toán giải khối Rubik
- Tự động dừng tìm kiếm sau 60 giây để tránh treo chương trình

## 🛠️ Công nghệ sử dụng | Technologies

- **Ngôn ngữ lập trình:** Python
- **Cấu trúc dữ liệu:** 
  - Hàng đợi ưu tiên (heapq)
  - Hàng đợi (deque)
  - Tập hợp (set, dict)
- **Thuật toán:**
  - A* (A-star) với hàm heuristic tùy chỉnh
  - Thuật toán tìm kiếm theo chiều rộng (BFS)

## 📋 Cấu trúc project | Project Structure

- `rubik_chen.py`: Định nghĩa trạng thái khối Rubik, các nước đi và hàm heuristic
- `rubik_solver.py`: Cài đặt thuật toán A* và BFS để giải khối Rubik

## ⚙️ Cách cài đặt | Installation

```bash
# Clone repository
git clone https://github.com/yourusername/final_rubik.git

# Di chuyển vào thư mục dự án
cd final_rubik

# Chạy chương trình
python rubik_solver.py
```

## 🚀 Cách sử dụng | Usage

1. **Định nghĩa trạng thái ban đầu:**
   ```python
   start_state = SOLVED_STATE.copy()
   # Áp dụng các bước di chuyển để tạo trạng thái xáo trộn
   start_state = apply_move(start_state, "R")
   start_state = apply_move(start_state, "U")
   ```

2. **Giải khối Rubik sử dụng A*:**
   ```python
   path, message = a_star(start_state)
   if path:
       print("Đường đi:", path)
       print(message)
       print("Số node đã duyệt:", dem_so_node)
   ```

3. **Giải khối Rubik sử dụng BFS:**
   ```python
   path, message = bfs(start_state)
   if path:
       print("Đường đi:", path)
       print(message)
       print("Số node đã duyệt:", dem_so_node)
   ```

## 🧠 Thuật toán giải | Solving Algorithms

### A* Search
Dự án sử dụng thuật toán A* với hàm heuristic tùy chỉnh để tối ưu hóa quá trình tìm kiếm. Hàm heuristic tính toán:
- Số khối góc và cạnh đặt sai vị trí
- Số khối góc và cạnh sai định hướng
Dự án này được phân phối dưới [Loại giấy phép]. Xem file `LICENSE` để biết thêm chi tiết.

---

<p align="center">💻 Happy Cubing! 🧩</p>
