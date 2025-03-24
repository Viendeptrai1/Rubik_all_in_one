# Rubik Cube Simulator

Chào mừng bạn đến với dự án Rubik Cube Simulator! Dự án này nhằm mục đích phát triển một ứng dụng Python để mô phỏng khối Rubik 3x3 với giao diện đồ họa 3D.

## Tính năng
- Hiển thị khối Rubik 3D với khả năng xoay và màu sắc đẹp.
- Xoay các mặt của khối Rubik với animation mượt mà.
- Nhập chuỗi nước đi theo ký hiệu tiêu chuẩn (F, B, R, L, U, D).
- Xáo trộn khối Rubik ngẫu nhiên.
- Giao diện người dùng trực quan với PyQt5.

## Cấu trúc dự án
- `main.py`: Tập tin chính để khởi động ứng dụng.
- `rubik.py`: Chứa lớp RubikCube và các phương thức liên quan.
- `rubik_widget.py`: Widget hiển thị khối Rubik với OpenGL.
- `controls_widget.py`: Widget chứa các điều khiển người dùng.

## Hướng dẫn cài đặt
1. Cài đặt Python và pip nếu chưa có.
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

## Cách chạy ứng dụng
- Chạy tập tin `main.py` để khởi động ứng dụng:
   ```bash
   python main.py
   ```

## Cách sử dụng
- Kéo chuột trái để xoay toàn bộ khối Rubik.
- Nhập các nước đi vào ô nhập liệu theo cú pháp chuẩn (ví dụ: "R U R' U'").
- Nhấn "Apply Moves" để áp dụng các nước đi.
- Nhấn "Reset" để đưa khối Rubik về trạng thái ban đầu.
- Nhấn "Shuffle" để xáo trộn khối Rubik ngẫu nhiên. 