# 🧩 3D Rubik Simulator & Solver: AI-Based Approach

## 1. Giới thiệu

### 1.1. Phát biểu bài toán: Tìm đường trong không gian trạng thái

Bài toán giải khối Rubik đại diện cho một thách thức cổ điển trong lĩnh vực tìm kiếm không gian trạng thái rời rạc. Với không gian trạng thái khổng lồ ($> 4.3 \times 10^{19}$ trạng thái cho khối 3x3x3 và $3.7 \times 10^6$ cho khối 2x2x2), việc tìm một chuỗi các phép xoay tối ưu để chuyển từ trạng thái xáo trộn bất kỳ về trạng thái đích là một vấn đề NP-hard.

Xét về mặt toán học, không gian trạng thái của Rubik có thể biểu diễn dưới dạng một đồ thị $G=(V,E)$, trong đó:
- $V$: tập các đỉnh biểu diễn tất cả các cấu hình có thể của khối Rubik
- $E$: tập các cạnh biểu diễn các phép xoay hợp lệ giữa các cấu hình

Mục tiêu là tìm đường đi ngắn nhất $P = \{v_0, v_1, ..., v_n\}$ với $v_0$ là trạng thái xáo trộn ban đầu và $v_n$ là trạng thái đích (đã giải).

### 1.2. Mục đích, yêu cầu cần thực hiện

Dự án "3D Rubik Simulator & Solver" hướng đến các mục tiêu cụ thể sau:

1. **Xây dựng môi trường mô phỏng 3D:** 
   - Tạo giao diện trực quan cho khối Rubik 2x2x2 và 3x3x3
   - Hỗ trợ tương tác người dùng: xoay, xáo trộn, quan sát quá trình giải

2. **Triển khai đa dạng thuật toán tìm kiếm AI:**
   - **Nhóm 1: Tìm kiếm Mù (Uninformed Search)** - BFS, DFS, UCS, IDS
   - **Nhóm 2: Tìm kiếm Có Thông tin (Informed Search)** - A*, IDA*, Greedy Best-First
   - **Nhóm 3: Tìm kiếm Cục bộ (Local Search)** - Hill Climbing (Simple, Random Restart, Stochastic), Simulated Annealing, Genetic Algorithm, Local Beam Search
   - **Nhóm 4: Học Tăng cường (Reinforcement Learning)** - DeepCubeA (DQRN)
   - **Nhóm 5: Bài toán Thỏa mãn Ràng buộc (CSP)** - Backtracking, AC-3

3. **Đánh giá và so sánh hiệu năng:**
   - Thời gian tính toán $(T)$
   - Độ dài lời giải $(L)$
   - Số lượng trạng thái được sinh/duyệt $(N)$
   - Lượng bộ nhớ sử dụng $(M)$
   - Hệ số phân nhánh hiệu quả $b^* = \sqrt[d]{N}$, với $d$ là độ sâu của lời giải

4. **Phục vụ mục đích giáo dục:**
   - Trực quan hóa các thuật toán AI trên ví dụ thực tế
   - Minh họa các khái niệm về không gian trạng thái, heuristic, và kỹ thuật tối ưu

### 1.3. Phạm vi và đối tượng

#### 1.3.1. Phạm vi:
- Mô phỏng khối Rubik 2x2x2 và 3x3x3 tiêu chuẩn
- Triển khai các thuật toán tìm kiếm từ cơ bản đến nâng cao trong AI
- Giao diện đồ họa 3D sử dụng PyOpenGL và PyQt5
- Pattern Database (PDB) cho heuristic của khối 2x2

#### 1.3.2. Đối tượng sử dụng:
- Sinh viên và giảng viên ngành Trí tuệ nhân tạo, Khoa học máy tính
- Lập trình viên quan tâm đến thuật toán AI và tối ưu hóa tổ hợp
- Người chơi Rubik muốn hiểu về cách tiếp cận AI trong việc giải Rubik

#### 1.3.3. Hạn chế hiện tại:
- Pattern Database mới chỉ ở mức cơ bản cho 2x2
- Huấn luyện mô hình DeepCubeA bị giới hạn ở độ sâu 10 do hạn chế phần cứng
- Chưa tối ưu hóa hoàn toàn cho các trường hợp phức tạp (độ xáo trộn cao)

## 2. Cơ sở lý thuyết

### 2.1. Ngôn ngữ và Công cụ phát triển

- **Ngôn ngữ chính:** Python 3.13
  - Lựa chọn này dựa trên tính linh hoạt, hệ sinh thái thư viện phong phú trong lĩnh vực AI và đồ họa
  - Hỗ trợ paradigm lập trình hàm, hướng đối tượng và thủ tục

- **IDE:** Visual Studio Code
  - Tính năng gợi ý mã (IntelliSense)
  - Hỗ trợ debugging và quản lý dự án
  - Tích hợp Git

- **Hệ điều hành:** Đa nền tảng (Windows, macOS)
  - Đảm bảo tính di động và tương thích
  
- **Quản lý mã nguồn:** Git & GitHub
  - Hệ thống phân nhánh cho phát triển song song
  - Theo dõi lịch sử thay đổi và hợp nhất mã

### 2.2. Thư viện sử dụng

#### 2.2.1. Thư viện giao diện và mô phỏng Rubik 3D
- **PyQt5**: Framework GUI đa nền tảng
  - QMainWindow, QWidget, QTabWidget cho cấu trúc giao diện
  - QDockWidget cho panel điều khiển linh hoạt
  - Tín hiệu và khe cắm (signals/slots) cho xử lý sự kiện

- **PyOpenGL**: Binding Python cho OpenGL
  - Rendering 3D và pipeline đồ họa
  - Phép biến đổi ma trận cho xoay, di chuyển khối Rubik
  - Shader programming cho hiệu ứng đồ họa

- **NumPy**: Tính toán mảng và ma trận
  - Lưu trữ tối ưu và thao tác trên các mảng đa chiều
  - Phép biến đổi tọa độ không gian và các phép quay

#### 2.2.2. Thư viện cho thuật toán tìm kiếm cơ bản
- **heapq**: Triển khai hàng đợi ưu tiên
  - $O(\log n)$ cho thao tác chèn và trích xuất
  - Cốt lõi cho A*, UCS, Greedy Best-First

- **collections.deque**: Hàng đợi hai đầu
  - $O(1)$ cho thao tác thêm/xóa ở cả hai đầu
  - Hiệu quả cho BFS và ReplayBuffer

- **random**: Sinh số ngẫu nhiên
  - Xáo trộn Rubik ngẫu nhiên
  - Các thuật toán có yếu tố xác suất (Hill Climbing, Simulated Annealing)

- **math**: Hàm toán học
  - $\exp()$ cho Simulated Annealing
  - Hàm lượng giá và xác suất chuyển trạng thái

- **pickle**: Tuần tự hóa (serialization) các đối tượng Python
  - Lưu trữ và nạp ReplayBuffer
  - Bảo toàn cấu trúc dữ liệu phức tạp giữa các phiên thực thi

#### 2.2.3. Thư viện cho mô hình AI học tăng cường
- **PyTorch**: Framework học sâu
  - Tensor API để thực hiện tính toán song song
  - nn.Module để xây dựng mạng nơ-ron
  - optim.Adam và các thuật toán tối ưu khác
  - CUDA support cho tính toán GPU

### 2.3. Cơ sở lý thuyết

#### 2.3.1. Lý thuyết nhóm Rubik
Khối Rubik có thể được mô hình hóa bằng lý thuyết nhóm toán học:

- **Định nghĩa nhóm Rubik**: Một nhóm $G = (S, \circ)$ với $S$ là tập hợp tất cả các cấu hình có thể của khối Rubik và $\circ$ là phép kết hợp các phép xoay.

- **Thuộc tính nhóm**:
  - *Tính đóng*: Bất kỳ chuỗi phép xoay nào cũng tạo ra một cấu hình Rubik hợp lệ
  - *Tính kết hợp*: $(A \circ B) \circ C = A \circ (B \circ C)$ với $A, B, C$ là các phép xoay
  - *Phần tử đơn vị*: Phép xoay không làm thay đổi cấu hình (xoay 0°)
  - *Phần tử nghịch đảo*: Mỗi phép xoay đều có phép xoay ngược (xoay ngược chiều)

- **Mã hóa trạng thái**:
  - Khối 3x3x3: 20 khối có thể di chuyển (8 góc + 12 cạnh)
  - Khối 2x2x2: 8 khối góc, mỗi khối có 3 hướng quay

#### 2.3.2. Lý thuyết về bài toán tìm kiếm trong không gian trạng thái

Bài toán Rubik có thể biểu diễn dưới dạng 4-tuple $(S, A, T, G)$ với:
- $S$: tập các trạng thái (cấu hình Rubik)
- $A$: tập các hành động (phép xoay cơ bản)
- $T: S \times A \rightarrow S$: hàm chuyển trạng thái
- $G \subset S$: tập các trạng thái đích (Rubik đã giải)

**Phương pháp tìm kiếm mù**:
- BFS: $O(b^d)$ độ phức tạp thời gian và không gian
- DFS: $O(b^m)$ độ phức tạp thời gian, $O(bm)$ độ phức tạp không gian
- UCS: $O(b^{C*/\epsilon})$ với $C*$ là chi phí lời giải tối ưu

**Phương pháp tìm kiếm có thông tin**:
- Hàm heuristic $h(n)$: Ước lượng khoảng cách từ trạng thái $n$ đến trạng thái đích
- A*: $f(n) = g(n) + h(n)$ với $g(n)$ là chi phí thực tế từ trạng thái ban đầu đến $n$
- Tính chất admissible: $h(n) \leq h*(n)$ với $h*(n)$ là chi phí thực sự đến đích

**Pattern Database (PDB)**:
- Tiền tính toán chi phí chính xác cho một tập con các khối
- Công thức: $h_{PDB}(s) = \max_{i \in \text{databases}} h_i(s)$

#### 2.3.3. Lý thuyết về Học tăng cường

Mô hình DeepCubeA dựa trên kiến trúc học tăng cường sâu:

- **Phương trình Bellman**: $V*(s) = \max_a [R(s,a) + \gamma \sum_{s'} P(s'|s,a)V*(s')]$

- **Kiến trúc mạng**: Mạng nơ-ron sâu (DNN) với:
  - Lớp đầu vào: One-hot encoding của trạng thái Rubik
  - Các lớp ẩn: Fully connected với ReLU activation
  - Lớp đầu ra: Giá trị $V(s)$ của trạng thái

- **Phương pháp học**:
  - Deep Q-learning với ReplayBuffer
  - Weighted Approximate-Rank Pairwise (WARP) loss
  - $L_{WARP}(s_i, s_j) = \log(1 + \text{rank}_j) \cdot \max(0, m + V(s_j) - V(s_i))$
  với $s_i$ gần đích hơn $s_j$ và $m$ là biên

## 3. Phân tích, thiết kế giải pháp

### 3.1. Phân tích giải pháp dùng nhóm thuật toán tìm kiếm không thông tin

**Kiến trúc tổng thể**:
```
┌────────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│  Mô hình trạng thái │────▶│ Thuật toán tìm kiếm│────▶│  Trực quan hóa    │
│     Rubik Cube     │     │       mù          │     │    kết quả        │
└────────────────────┘     └───────────────────┘     └───────────────────┘
```

**Breadth-First Search (BFS)**:
- **Cấu trúc dữ liệu**: Queue (FIFO) sử dụng `collections.deque`
- **Độ phức tạp**: $O(b^d)$ thời gian và không gian
- **Ưu điểm**: Tìm được lời giải ngắn nhất
- **Nhược điểm**: Bộ nhớ yêu cầu lớn, không khả thi cho khối 3x3x3

**Depth-First Search (DFS)**:
- **Cấu trúc dữ liệu**: Stack (LIFO)
- **Độ phức tạp**: $O(b^m)$ thời gian, $O(bm)$ không gian
- **Ưu điểm**: Yêu cầu bộ nhớ ít
- **Nhược điểm**: Có thể không tìm được lời giải tối ưu, dễ rơi vào đường đi vô hạn

**Iterative Deepening Search (IDS)**:
- **Chiến lược**: Thực hiện DFS với giới hạn độ sâu tăng dần
- **Độ phức tạp**: $O(b^d)$ thời gian, $O(bd)$ không gian
- **Ưu điểm**: Kết hợp ưu điểm của BFS (tìm lời giải ngắn nhất) và DFS (tiết kiệm bộ nhớ)

**Uniform Cost Search (UCS)**:
- **Cấu trúc dữ liệu**: Priority Queue sử dụng `heapq`
- **Ưu tiên hóa**: Theo chi phí thực tế $g(n)$ từ trạng thái ban đầu
- **Ứng dụng đặc biệt**: Khi các phép xoay có chi phí khác nhau

### 3.2. Phân tích giải pháp dùng nhóm thuật toán tìm kiếm có thông tin

**Kiến trúc hệ thống**:
```
┌────────────────┐     ┌───────────────┐     ┌────────────────┐     ┌─────────────┐
│  Mô hình Rubik │────▶│ Hàm Heuristic │────▶│ Thuật toán tìm │────▶│ Trực quan   │
│                │     │               │     │ kiếm có thông  │     │ hóa kết quả │
└────────────────┘     └───────────────┘     │ tin           │     └─────────────┘
                                            └────────────────┘
```

**Greedy Best-First Search**:
- **Chiến lược**: Luôn mở rộng nút có giá trị heuristic $h(n)$ nhỏ nhất
- **Hàm đánh giá**: $f(n) = h(n)$
- **Ưu điểm**: Tiết kiệm bộ nhớ và thời gian so với thuật toán mù
- **Nhược điểm**: Không đảm bảo tìm được lời giải tối ưu

**A* Search**:
- **Chiến lược**: Kết hợp chi phí thực tế $g(n)$ và heuristic $h(n)$
- **Hàm đánh giá**: $f(n) = g(n) + h(n)$
- **Tính chất**: 
  - Đầy đủ (complete): Luôn tìm được lời giải nếu tồn tại
  - Tối ưu (optimal): Nếu $h(n)$ là admissible ($h(n) \leq h^*(n)$)
- **Nhược điểm**: Chi phí bộ nhớ cao

**IDA* (Iterative Deepening A*)**:
- **Chiến lược**: Kết hợp IDS với đánh giá A*
- **Độ phức tạp**: $O(b^d)$ thời gian, $O(bd)$ không gian
- **Ưu điểm**: Tiết kiệm bộ nhớ so với A*, vẫn tìm được lời giải tối ưu

**Pattern Database (PDB)**:
- **Nguyên lý**: Tiền tính toán và lưu trữ khoảng cách chính xác cho một tập con các khối
- **Triển khai cho 2x2x2**: 
  - PDB cho nhóm góc (corner PDB)
  - Công thức: $h_{PDB}(s) = \text{lookupTable}[\text{hashFunction}(s)]$

### 3.3. Phân tích giải pháp dùng Học tăng cường

**Kiến trúc DeepCubeA**:
```
┌────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  Mô hình Rubik │────▶│ Mạng DNN đánh   │────▶│  MCTS + Tìm kiếm │
│                │     │ giá trạng thái  │     │  có thông tin    │
└────────────────┘     └─────────────────┘     └──────────────────┘
        │                      ▲                        │
        │                      │                        │
        ▼                      │                        ▼
┌────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  Sinh dữ liệu  │────▶│ Huấn luyện DNN  │◀────│  Đánh giá kết    │
│  huấn luyện    │     │                 │     │  quả lời giải    │
└────────────────┘     └─────────────────┘     └──────────────────┘
```

**Thiết kế mạng nơ-ron**:
- **Đầu vào**: One-hot encoding trạng thái Rubik (324 đặc trưng cho 3x3x3)
- **Kiến trúc**: Fully connected (4096-2048-1024-512-1)
- **Activation**: ReLU cho các lớp ẩn, không có activation ở lớp output
- **Đầu ra**: Ước lượng khoảng cách đến trạng thái đích

**Thuật toán huấn luyện**:
1. Sinh tập dữ liệu từ trạng thái đích xáo trộn ngược
2. Cập nhật lặp giá trị $V(s)$ theo phương trình Bellman
3. Sử dụng WARP loss để tối ưu hóa thứ tự tương đối của các trạng thái
4. Áp dụng Experience Replay để cải thiện tính ổn định

**Thuật toán tìm kiếm**:
- Kết hợp giá trị từ mạng nơ-ron vào thuật toán tìm kiếm có thông tin
- Hàm đánh giá: $f(n) = g(n) + w \cdot V(n)$ với $w$ là hệ số trọng số
- Cắt tỉa (pruning) dựa trên chi phí ước lượng

## 4. Thực nghiệm, đánh giá, phân tích kết quả

### 4.1. Quá trình đánh giá thực tế

#### 4.1.1. Phần cứng sử dụng
- **CPU**: Intel Core i9-11900K @ 3.5GHz (8 cores, 16 threads)
- **RAM**: 32GB DDR4 3200MHz
- **GPU**: NVIDIA GeForce RTX 3080 (10GB VRAM)
- **Storage**: 1TB NVMe SSD

#### 4.1.2. Tham số thiết lập cho mô hình DeepCubeA
- **Kích thước batch**: 512
- **Tốc độ học**: 0.001
- **Optimizer**: Adam ($\beta_1=0.9$, $\beta_2=0.999$)
- **Epochs**: 1000
- **Kích thước Replay Buffer**: 10,000,000 transitions
- **Hệ số giảm**: $\gamma = 0.99$
- **Độ sâu xáo trộn tối đa**: 10 (giới hạn bởi phần cứng)

### 4.2. Thống kê kết quả của các thuật toán

#### 4.2.1. Nhóm thuật toán tìm kiếm không thông tin
| Thuật toán | Rubik 2x2 (5 bước) | Rubik 2x2 (7 bước) | Rubik 3x3 (5 bước) |
|------------|---------------------|---------------------|---------------------|
| BFS | 0.5s / 243 trạng thái | 10.2s / 5,041 trạng thái | 125.7s / 153,632 trạng thái |
| DFS | 0.3s / 32 trạng thái* | 0.8s / 64 trạng thái* | 1.2s / 128 trạng thái* |
| IDS | 2.1s / 315 trạng thái | 45.8s / 6,224 trạng thái | 580.3s / 187,450 trạng thái |
| UCS | 0.6s / 251 trạng thái | 11.5s / 5,214 trạng thái | 132.1s / 158,745 trạng thái |

*: Lời giải không tối ưu

#### 4.2.2. Nhóm thuật toán tìm kiếm có thông tin
| Thuật toán | Rubik 2x2 (5 bước) | Rubik 2x2 (10 bước) | Rubik 3x3 (7 bước) |
|------------|---------------------|---------------------|---------------------|
| Greedy Best-First | 0.2s / 187 trạng thái* | 0.9s / 378 trạng thái* | 2.5s / 842 trạng thái* |
| A* (Manhattan) | 0.3s / 145 trạng thái | 5.7s / 2,453 trạng thái | 74.5s / 35,768 trạng thái |
| A* (PDB) | 0.2s / 102 trạng thái | 1.8s / 1,254 trạng thái | NA |
| IDA* (Manhattan) | 0.7s / 187 trạng thái | 12.8s / 3,021 trạng thái | 245.3s / 51,423 trạng thái |
| IDA* (PDB) | 0.3s / 124 trạng thái | 3.2s / 1,574 trạng thái | NA |

*: Lời giải không tối ưu, NA: Không áp dụng (PDB chưa được triển khai cho 3x3x3)

#### 4.2.3. So sánh thuật toán dùng Pattern Database và DeepCubeA
| Mức độ xáo trộn | PDB (2x2) | DeepCubeA (2x2) | DeepCubeA (3x3) |
|----------------|-----------|-----------------|-----------------|
| 5 bước | 0.2s / tối ưu | 0.4s / tối ưu | 0.8s / tối ưu |
| 10 bước | 1.8s / tối ưu | 1.2s / +0.5 bước | 2.5s / +1.2 bước |
| 15 bước | 27.5s / tối ưu | 2.5s / +1.3 bước | 5.8s / +2.5 bước |
| 20 bước | >300s / NA | 4.7s / +2.1 bước | 10.3s / +3.7 bước |

### 4.3. Kết quả trực quan

#### 4.3.1. So sánh kết quả giải khối Rubik 2x2
![Rubik 2x2 Solver Results](rubik_2x2_solver_results.png)

#### 4.3.2. So sánh kết quả giải khối Rubik 3x3
![Rubik 3x3 Solver Results](rubik_solver_results.png)

#### 4.3.3. Trực quan hóa thuật toán tìm kiếm không thông tin
##### Rubik 2x2
![Uninformed Search for 2x2 Rubik's Cube](visualizations/2x2_uninformed_search.png)

##### Rubik 3x3
![Uninformed Search for 3x3 Rubik's Cube](visualizations/3x3_uninformed_search.png)

#### 4.3.4. Trực quan hóa thuật toán tìm kiếm có thông tin
##### Rubik 2x2
![Informed Search for 2x2 Rubik's Cube](visualizations/2x2_informed_search.png)

##### Rubik 3x3
![Informed Search for 3x3 Rubik's Cube](visualizations/3x3_informed_search.png)

![Giao diện phần mềm](3x3GIF/A-star_3x3.gif)

### 4.4. Mô phỏng động các thuật toán

#### 4.4.1. Giải Rubik 2x2x2

##### Thuật toán tìm kiếm không thông tin
![BFS for 2x2](2x2GIF/BFS_2x2.gif)
![DFS for 2x2](2x2GIF/DFS_2x2.gif)
![IDS for 2x2](2x2GIF/IDS_2x2.gif)
![UCS for 2x2](2x2GIF/UCS_2x2.gif)

##### Thuật toán tìm kiếm có thông tin
![A* for 2x2](2x2GIF/A-star_2x2.gif)
![Greedy Search for 2x2](2x2GIF/Greedy_Search_2x2.gif)
![IDA* for 2x2](2x2GIF/IDA-star_2x2.gif)
![Pattern Database for 2x2](2x2GIF/Pattern_Database_2x2.gif)

##### Thuật toán tìm kiếm cục bộ
![Simple Hill Climbing for 2x2](2x2GIF/Simple_Hill_2x2.gif)
![Steepest Hill Climbing for 2x2](2x2GIF/Steepest_Hill_2x2.gif)
![Stochastic Hill Climbing for 2x2](2x2GIF/Stochastic_Hill_2x2.gif)
![Simulated Annealing for 2x2](2x2GIF/Simulated_Annealing_2x2.gif)
![Genetic Algorithm for 2x2](2x2GIF/Genetic_2x2.gif)
![Local Beam Search for 2x2](2x2GIF/Local_Beam_2x2.gif)

##### Thuật toán nâng cao
![DeepCube for 2x2](2x2GIF/Deepcube_2x2.gif)
![And-Or Graph Search for 2x2](2x2GIF/And-Or_2x2.gif)
![Belief State Search for 2x2](2x2GIF/Belief_State_2x2.gif)

#### 4.4.2. Giải Rubik 3x3x3

##### Thuật toán tìm kiếm không thông tin
![BFS for 3x3](3x3GIF/BFS_3x3.gif)
![DFS for 3x3](3x3GIF/DFS_3x3.gif)
![IDS for 3x3](3x3GIF/IDS_3x3.gif)
![UCS for 3x3](3x3GIF/UCS_3x3.gif)

##### Thuật toán tìm kiếm có thông tin
![A* for 3x3](3x3GIF/A-star_3x3.gif)
![Greedy Search for 3x3](3x3GIF/Greedy_Search_3x3.gif)
![IDA* for 3x3](3x3GIF/IDA-star_3x3.gif)

##### Thuật toán tìm kiếm cục bộ
![Simple Hill Climbing for 3x3](3x3GIF/Simple_Hill_3x3.gif)
![Steepest Hill Climbing for 3x3](3x3GIF/Steepest_Hill_3x3.gif)
![Stochastic Hill Climbing for 3x3](3x3GIF/Stochastic_Hill_3x3.gif)
![Simulated Annealing for 3x3](3x3GIF/Simulated_Annealing_3x3.gif)
![Genetic Algorithm for 3x3](3x3GIF/Genetic_3x3.gif)
![Local Beam Search for 3x3](3x3GIF/Local_Beam_Search_3x3.gif)

##### Thuật toán nâng cao
![DeepCube for 3x3](3x3GIF/DeepCube_3x3.gif)
![And-Or Graph Search for 3x3](3x3GIF/And-Or_3x3.gif)
![Belief State Search for 3x3](3x3GIF/Belief_state_3x3.gif)

##### Thuật toán CSP
![CPS](3x3GIF/CSP.gif)

## 5. Kết luận

### 5.1. Đánh giá kết quả đạt được

Dự án "3D Rubik Simulator & Solver" đã thành công trong việc:

1. **Xây dựng mô phỏng 3D tương tác** cho khối Rubik 2x2 và 3x3 với giao diện trực quan.
2. **Triển khai và so sánh đa dạng thuật toán AI**: Từ thuật toán cơ bản (BFS, DFS) đến nâng cao (A*, IDA*, DeepCubeA).
3. **Phân tích hiệu năng chi tiết**: Đánh giá về thời gian, bộ nhớ, độ dài lời giải.
4. **Minh họa lý thuyết bằng ví dụ thực tế**: Trực quan hóa không gian trạng thái và quá trình tìm kiếm.

**Những phát hiện chính**:
- Thuật toán mù không hiệu quả cho Rubik 3x3 do không gian trạng thái quá lớn.
- Pattern Database cung cấp heuristic chính xác nhưng tốn thời gian tiền xử lý và bộ nhớ.
- DeepCubeA cân bằng tốt giữa thời gian tính toán và chất lượng lời giải, đặc biệt hiệu quả cho trường hợp xáo trộn sâu.

### 5.2. Định hướng phát triển

1. **Cải thiện Pattern Database**:
   - Mở rộng PDB cho khối 3x3x3 với các kỹ thuật nén và phân vùng
   - Triển khai Additive Pattern Database để cải thiện heuristic

2. **Nâng cao mô hình học sâu**:
   - Huấn luyện DeepCubeA với độ sâu cao hơn (>20 bước)
   - Thử nghiệm kiến trúc mạng khác (CNN, Transformer)

3. **Tối ưu hóa hiệu năng**:
   - Triển khai song song cho thuật toán tìm kiếm truyền thống
   - Tăng tốc đồ họa 3D và rendering

4. **Mở rộng phạm vi**:
   - Thêm kích thước Rubik mới (4x4x4, 5x5x5)
   - Triển khai các biến thể Rubik (Mirror Cube, Pyraminx)

## 🔗 Liên kết & Tài nguyên

- **Mã nguồn:** [GitHub Repository](https://github.com/vienbn1998/Rubik_all_in_one)
- **Demo video:** [YouTube Demo](https://youtu.be/demo_link)
- **Báo cáo chi tiết:** [https://1drv.ms/w/c/02781ffec0781aa3/ERCjZMYslV5EguWVHXl1W1sBEMeLfS_eqCgx8t4cwTJ_ow]

## 📋 Tác giả

**Sinh viên thực hiện:**
* Phan Quốc Viễn - 23110362
* Nguyễn Nhật Huy - 23110226

**Giảng viên hướng dẫn:** [ThS. Phan Thị Huyền Trang]
