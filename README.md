# Rubik Cube Simulator

Chào mừng bạn đến với dự án Rubik Cube Simulator! Dự án này nhằm mục đích phát triển một ứng dụng Python để mô phỏng khối Rubik 3x3 và 2x2 với giao diện đồ họa 3D, đồng thời triển khai các thuật toán tìm kiếm để giải Rubik tự động.

## Tính năng
- Hiển thị khối Rubik 3D với khả năng xoay và màu sắc đẹp.
- Xoay các mặt của khối Rubik với animation mượt mà.
- Nhập chuỗi nước đi theo ký hiệu tiêu chuẩn (F, B, R, L, U, D).
- Xáo trộn khối Rubik ngẫu nhiên.
- Giao diện người dùng trực quan với PyQt5.
- Hỗ trợ cả khối Rubik 3x3 và 2x2
- Biểu diễn trạng thái Rubik thông qua hoán vị (permutation) và hướng (orientation)
- Thuật toán tìm kiếm tự động giải Rubik: BFS và A*

## Biểu diễn trạng thái Rubik
Dự án sử dụng cách biểu diễn trạng thái Rubik dựa trên:

### Hoán vị (Permutation)
- **Corner Permutation (cp)**: Vị trí của 8 góc khối Rubik
  - 0=URF, 1=ULF, 2=ULB, 3=URB, 4=DRF, 5=DLF, 6=DLB, 7=DRB
  - U=Up (trên), D=Down (dưới), R=Right (phải), L=Left (trái), F=Front (trước), B=Back (sau)
- **Edge Permutation (ep)**: Vị trí của 12 cạnh khối Rubik (chỉ có trong Rubik 3x3)
  - 0=UR, 1=UF, 2=UL, 3=UB, 4=DR, 5=DF, 6=DL, 7=DB, 8=FR, 9=FL, 10=BL, 11=BR

### Hướng (Orientation)
- **Corner Orientation (co)**: Hướng của các góc
  - 0=đúng hướng, 1=xoay theo chiều kim đồng hồ một lần, 2=xoay theo chiều kim đồng hồ hai lần
- **Edge Orientation (eo)**: Hướng của các cạnh (chỉ có trong Rubik 3x3)
  - 0=đúng hướng, 1=lật ngược

Cách biểu diễn này cho phép triển khai các thuật toán tìm kiếm hiệu quả và tính toán hàm heuristic phù hợp.

## Cấu trúc dự án
- `main.py`: Tập tin chính để khởi động ứng dụng.
- `rubik_3x3.py`: Triển khai khối Rubik 3x3 cho giao diện 3D
- `rubik_2x2.py`: Triển khai khối Rubik 2x2 cho giao diện 3D
- `rubik_widget.py`: Widget hiển thị khối Rubik với OpenGL.
- `controls_widget.py`: Widget chứa các điều khiển người dùng.
- `RubikState/`: Thư mục chứa các lớp biểu diễn trạng thái Rubik và thuật toán giải
  - `rubik_chen.py`: Lớp biểu diễn trạng thái Rubik 3x3 sử dụng hoán vị và hướng
  - `rubik_2x2.py`: Lớp biểu diễn trạng thái Rubik 2x2 sử dụng hoán vị và hướng
  - `rubik_solver.py`: Triển khai các thuật toán giải Rubik (BFS, A*)

## Lộ trình phát triển

### Giai đoạn 1: Xây dựng nền tảng mô phỏng (Hoàn thành)
- [x] Phát triển giao diện đồ họa 3D cho khối Rubik 3x3 và 2x2
- [x] Triển khai chức năng xoay các mặt với animation
- [x] Xây dựng biểu diễn trạng thái Rubik sử dụng hoán vị và hướng
- [x] Triển khai chức năng xáo trộn ngẫu nhiên

### Giai đoạn 2: Thuật toán tìm kiếm không thông tin (Hoàn thành một phần)
- [x] Triển khai thuật toán BFS (Breadth-First Search)
- [ ] Tối ưu hóa quá trình tìm kiếm để xử lý các trạng thái phức tạp
- [ ] Hiển thị quá trình tìm kiếm và các thống kê (số bước, thời gian, bộ nhớ)

### Giai đoạn 3: Thuật toán tìm kiếm có thông tin (Hoàn thành một phần)
- [x] Triển khai thuật toán A* (A-star)
- [x] Xây dựng hàm heuristic cho khối Rubik
- [ ] Cải thiện hàm heuristic và tối ưu hóa thuật toán
- [ ] Hiển thị trực quan quá trình tìm kiếm của A*

### Giai đoạn 4: Mô hình CSP (Constraint Satisfaction Problem)
- [ ] Mô hình hóa bài toán Rubik dưới dạng CSP
- [ ] Định nghĩa các biến, miền giá trị, và ràng buộc
- [ ] Triển khai các kỹ thuật như forward checking và arc consistency
- [ ] So sánh hiệu quả với các phương pháp tìm kiếm trước đó

### Giai đoạn 5: Giải pháp Machine Learning
- [ ] Xây dựng mô hình học máy để giải Rubik
- [ ] Thu thập dữ liệu từ các lời giải đã biết
- [ ] Huấn luyện mô hình dự đoán nước đi tối ưu
- [ ] Kết hợp với tìm kiếm để tăng hiệu quả giải

### Giai đoạn 6: Reinforcement Learning
- [ ] Triển khai giải pháp Reinforcement Learning
- [ ] Thiết kế môi trường và hàm phần thưởng cho Rubik
- [ ] Huấn luyện mô hình RL (Deep Q-Network hoặc Policy Gradient)
- [ ] So sánh hiệu quả với các phương pháp khác

### Giai đoạn 7: Tích hợp và hoàn thiện
- [ ] Tích hợp tất cả thuật toán vào giao diện chính
- [ ] Thêm chức năng so sánh trực quan giữa các thuật toán
- [ ] Tối ưu hóa hiệu suất và trải nghiệm người dùng
- [ ] Viết tài liệu chi tiết và hướng dẫn sử dụng

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
- Chuyển đổi giữa Rubik 3x3 và 2x2 bằng cách sử dụng tab 