# Rubik All-in-One

Ứng dụng giả lập và giải khối Rubik với nhiều thuật toán.

## Tính năng chính

- Hỗ trợ khối Rubik 3x3 và 2x2
- Giao diện 3D tương tác sử dụng OpenGL
- Nhiều thuật toán giải khác nhau
- Khả năng mở rộng thuật toán dễ dàng
- Tách luồng UI và giải thuật để giao diện không bị đóng băng

## Cách cài đặt

1. Cài đặt Python 3.7 trở lên
2. Cài đặt các thư viện phụ thuộc:
   ```
   pip install -r requirements.txt
   ```
3. Chạy ứng dụng:
   ```
   python main.py
   ```

## Cách sử dụng

- Chọn loại Rubik 2x2 hoặc 3x3 bằng cách chuyển tab
- Sử dụng chuột để xoay khối Rubik
- Nhập ký hiệu nước đi (F, R, U, L, B, D) và áp dụng
- Chọn thuật toán giải và nhấn "Giải Rubik"
- Xem kết quả và áp dụng lời giải

## Hướng dẫn thêm thuật toán mới

Ứng dụng được thiết kế để dễ dàng thêm các thuật toán mới. Dưới đây là các bước cần thực hiện:

### 1. Thêm cài đặt thuật toán

Thêm triển khai thuật toán của bạn vào `RubikState/rubik_solver_2x2.py` và/hoặc `RubikState/rubik_solver_3x3.py`. Sau đó, đăng ký hàm wrapper trong `RubikState/rubik_solver.py`. Ví dụ:

```python
# Trong rubik_solver_2x2.py
def my_new_algorithm_2x2(state, time_limit=30):
    # Triển khai thuật toán của bạn
    path = []  # Đường đi tìm được
    nodes_visited = 0  # Số nút đã duyệt
    time_taken = 0.0  # Thời gian thực thi
    return path, nodes_visited, time_taken

# Trong rubik_solver_3x3.py
def my_new_algorithm_3x3(state, time_limit=30):
    # Triển khai thuật toán của bạn
    path = []
    nodes_visited = 0
    time_taken = 0.0
    return path, nodes_visited, time_taken

# Trong rubik_solver.py
def my_new_algorithm(state, time_limit=30):
    """Mô tả thuật toán mới của bạn"""
    if isinstance(state, Rubik2x2State):
        return my_new_algorithm_2x2(state, time_limit=time_limit)
    return my_new_algorithm_3x3(state, time_limit=time_limit)
```

Sau đó, xuất hàm wrapper trong `rubik_solver.py`:

```python
from RubikState.rubik_solver_2x2 import my_new_algorithm_2x2
from RubikState.rubik_solver_3x3 import my_new_algorithm_3x3
# ...
__all__ = ['bfs', 'dfs', ... 'my_new_algorithm']
```

### 2. Thêm thuật toán vào giao diện

Thêm thuật toán vào `controls_widget.py` trong hai vị trí chính:

1. Thêm vào registry trong hàm `get_algorithm_registry()`:

```python
def get_algorithm_registry(self):
    """Đăng ký thuật toán - dễ dàng mở rộng trong tương lai"""
    return {
        # ...thuật toán hiện có
        11: ("My New Algorithm", "my_new_algorithm")  # ID tiếp theo, tên hiển thị, tên hàm
    }
```

2. Thêm vào ánh xạ tên thuật toán với hàm trong `solve_rubik()`:

```python
algorithm_funcs = {
    # ...thuật toán hiện có
    "my_new_algorithm": my_new_algorithm,
}
```

### 3. Thêm nút radio cho thuật toán

Thêm radio button cho thuật toán mới trong phần `init_ui()`, vào nhóm thuật toán phù hợp:

```python
# Thêm radio button mới
self.my_new_algorithm_radio = QRadioButton("My New Algorithm")
self.algorithm_button_group.addButton(self.my_new_algorithm_radio, 11)  # ID phải khớp với registry

# Thêm vào layout của nhóm thuật toán phù hợp
appropriate_group_layout.addWidget(self.my_new_algorithm_radio)
```

### 4. Kiểm thử thuật toán

Kiểm tra thuật toán mới với các tình huống khác nhau để đảm bảo hoạt động chính xác và hiệu quả.

## Cấu trúc dự án

- `main.py`: Điểm khởi đầu ứng dụng
- `rubik_widget.py`: Widget hiển thị Rubik 3D
- `controls_widget.py`: Widget điều khiển và giao diện người dùng
- `rubik_3x3.py`, `rubik_2x2.py`: Mô phỏng 3D của khối Rubik
- `RubikState/`: Thư mục chứa các thuật toán và biểu diễn trạng thái
  - `rubik_chen.py`, `rubik_2x2.py`: Biểu diễn trạng thái cho khối Rubik
  - `rubik_solver.py`: Giao diện thống nhất cho các thuật toán
  - `rubik_solver_2x2.py`, `rubik_solver_3x3.py`: Triển khai cụ thể cho từng loại Rubik

## Đóng góp

Đóng góp và cải tiến cho dự án luôn được chào đón. Vui lòng tạo issue hoặc pull request để thêm cải tiến mới.

## Giấy phép

[MIT License](LICENSE)
