# Phân Tích Thuật Toán AI Trên Khối Rubik

Nền tảng nghiên cứu học thuật để phân tích toàn diện hiệu suất các thuật toán trí tuệ nhân tạo cho bài toán khối Rubik.

## Mục Tiêu Nghiên Cứu

Dự án cung cấp nền tảng để đánh giá và so sánh hiệu suất của nhiều thuật toán tìm kiếm AI khác nhau khi áp dụng vào bài toán khối Rubik. Hệ thống thu thập các chỉ số hiệu suất chi tiết cho từng thuật toán, giúp:

- So sánh hiệu quả và độ phức tạp của nhiều chiến lược tìm kiếm
- Phân tích đặc tính heuristic và ảnh hưởng đến hiệu suất thuật toán
- Đánh giá tốc độ hội tụ của các phương pháp tìm kiếm cục bộ
- Trực quan hóa quá trình tìm kiếm và không gian trạng thái

## Chỉ Số Phân Tích

Hệ thống theo dõi và phân tích các chỉ số hiệu suất chính:

### Chỉ Số Hiệu Suất Cơ Bản
- **Thời gian thực thi**: Thời gian tìm kiếm lời giải (giây)
- **Số nút đã duyệt**: Số lượng trạng thái được khám phá
- **Độ dài lời giải**: Số lượng bước tối thiểu để đạt đến trạng thái đích

### Chỉ Số Hiệu Suất Nâng Cao
- **Bộ nhớ sử dụng**: Số lượng trạng thái được lưu trữ trong bộ nhớ cùng lúc
- **Hệ số phân nhánh hiệu quả**: Tỷ lệ giữa số trạng thái được tạo ra và số nút đã duyệt
- **Tỷ lệ cắt tỉa**: Phần trăm trạng thái được loại bỏ không cần xem xét thêm

### Phân Tích Heuristic
- **Độ chính xác heuristic**: Mức độ dự đoán chính xác về khoảng cách tới đích
- **Giá trị heuristic trung bình**: Trung bình của các giá trị heuristic được tính
- **Thống kê lời gọi heuristic**: Tần suất và hiệu quả của hàm heuristic

### Chỉ Số Thuật Toán Đặc Biệt
- **Nhiệt độ** (Simulated Annealing): Đường cong nhiệt độ theo thời gian
- **Đa dạng quần thể** (Genetic Algorithm): Mức độ đa dạng của quần thể
- **Các ngưỡng tìm kiếm** (IDA*): Các ngưỡng được sử dụng trong quá trình tìm kiếm

## Các Thuật Toán Đã Triển Khai

### Thuật Toán Tìm Kiếm Không Heuristic
- ✅ Tìm Kiếm Theo Chiều Rộng (BFS)
- ✅ Tìm Kiếm Theo Chiều Sâu (DFS)
- ✅ Tìm Kiếm Chi Phí Đồng Nhất (UCS)
- ✅ Tìm Kiếm Sâu Dần (IDS)

### Thuật Toán Tìm Kiếm Có Heuristic
- ✅ Tìm Kiếm A*
- ✅ Tìm Kiếm IDA* (A* Sâu Dần)
- ✅ Tìm Kiếm Tham Lam (Greedy Best-First)

### Thuật Toán Tìm Kiếm Cục Bộ
- ✅ Leo Đồi (Steepest Ascent)
- ✅ Leo Đồi với Khởi Động Lại Ngẫu Nhiên
- ⏳ Mô Phỏng Luyện Kim (Simulated Annealing) - Đang phát triển
- ⏳ Thuật Toán Di Truyền (Genetic Algorithm) - Đang phát triển
- ⏳ Tìm Kiếm Chùm Cục Bộ (Local Beam Search) - Đang phát triển

### Tìm Kiếm Trong Môi Trường Phức Tạp
- ⏳ Tìm Kiếm Đồ Thị AND-OR - Đang phát triển
- ⏳ Tìm Kiếm Trạng Thái Niềm Tin (Belief States) - Đang phát triển

### Tiếp Cận Bài Toán Thỏa Mãn Ràng Buộc
- ⏳ Thuật Toán Kiểm Tra Tính Nhất Quán AC-3 - Đang phát triển
- ⏳ Tìm Kiếm Quay Lui (Gán Biến) - Đang phát triển
- ⏳ Tìm Kiếm Quay Lui (Kiểm Tra Trước) - Đang phát triển

### Kỹ Thuật Nâng Cao
- ✅ A* với Cơ Sở Dữ Liệu Mẫu (Pattern Database) cho khối 2×2
- ⏳ Mạng Q Sâu (DQN) - Đang phát triển

## Thuật Toán Dự Kiến (TODO)
- ⏳ Tìm Kiếm Cây Monte Carlo (MCTS)
- ⏳ Phương Pháp Độ Dốc Chính Sách (Policy Gradient)
- ⏳ Tìm Kiếm Hai Chiều (Bidirectional Search)
- ⏳ Cơ Sở Dữ Liệu Mẫu Động (Dynamic Pattern Database)
- ⏳ Tìm Kiếm Biên (Frontier Search - Phiên Bản Tiết Kiệm Bộ Nhớ)

## Kiến Trúc Dự Án

- `main.py`: Điểm khởi đầu ứng dụng và cấu trúc giao diện chính
- `rubik_widget.py`: Các thành phần trực quan hóa 3D khối Rubik với OpenGL/PyQt5
- `controls_widget.py`: Giao diện nghiên cứu, cấu hình thuật toán và hiển thị chỉ số phân tích
- `RubikState/`:
  - `rubik_chen.py`, `rubik_2x2.py`: Biểu diễn trạng thái và phép biến đổi khối Rubik
  - `rubik_solver.py`: Giao diện thuật toán thống nhất
  - `rubik_solver_2x2.py`, `rubik_solver_3x3.py`: Cài đặt thuật toán cho từng kích thước cụ thể

## Ứng Dụng Học Thuật

Nền tảng này phù hợp cho:
- Nghiên cứu hiệu suất thuật toán AI trên không gian trạng thái lớn
- Phân tích so sánh các chiến lược tìm kiếm và heuristic
- Giảng dạy về các thuật toán tìm kiếm AI và cấu trúc dữ liệu
- Khám phá trực quan quá trình giải quyết vấn đề của AI

## Giấy Phép

[Giấy Phép MIT](LICENSE)
