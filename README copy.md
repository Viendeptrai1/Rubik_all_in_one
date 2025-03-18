# Rubik Solver

Chào mừng bạn đến với dự án Rubik Solver! Dự án này nhằm mục đích phát triển một ứng dụng Python để mô phỏng và giải Rubik 2x2 và 3x3 với giao diện đồ họa 3D hiện đại.

## Mục tiêu
- Hiển thị khối Rubik 3D (2x2 và 3x3) với khả năng xoay và màu sắc đẹp.
- Nhận diện 6 mặt Rubik bằng camera (dùng OpenCV).
- Hỗ trợ nhiều thuật toán giải (newbie cho 2x2, kociemba cho 3x3).
- Giao diện người dùng (Dear PyGui) với hai chế độ xuất kết quả: từng bước và tự động xoay với animation.

## Cấu trúc dự án
- `main.py`: Tập tin chính để khởi động ứng dụng.
- `rubik.py`: Chứa lớp RubikCube và các phương thức liên quan.
- `README.md`: Tài liệu hướng dẫn và thông tin về dự án.

## Hướng dẫn cài đặt
1. Cài đặt Python và pip nếu chưa có.
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install pygame PyOpenGL
   ```

## Cách chạy ứng dụng
- Chạy tập tin `main.py` để khởi động ứng dụng.

## Ghi chú
- Dự án đang trong quá trình phát triển, vui lòng theo dõi để cập nhật các tính năng mới! 