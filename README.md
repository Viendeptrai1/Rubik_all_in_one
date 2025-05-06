# 🧩 3D Rubik Simulator & Solver 🤖

Dự án mô phỏng khối Rubik 3D (2x2x2 và 3x3x3) và triển khai, so sánh hiệu quả của các thuật toán Trí tuệ Nhân tạo (AI) để tìm lời giải.

**Sinh viên thực hiện:**
* Phan Quốc Viễn - 23110362
* Nguyễn Nhật Huy - 23110226

**Giảng viên hướng dẫn:** [Tên giảng viên]

---

## 📜 Tổng quan Dự án

Khối Rubik là một bài toán tổ hợp kinh điển với không gian trạng thái khổng lồ ($> 4.3 \times 10^{19}$ cho 3x3x3), là một thử thách thú vị cho các thuật toán tìm kiếm AI. Dự án này cung cấp:
* **Môi trường mô phỏng 3D tương tác:** Cho phép xoay, xáo trộn và quan sát quá trình giải Rubik.
* **Triển khai đa dạng thuật toán AI:** Từ tìm kiếm mù, có thông tin, tìm kiếm cục bộ đến học tăng cường.
* **Công cụ đánh giá và so sánh:** Phân tích hiệu năng các thuật toán dựa trên thời gian, số bước, bộ nhớ,...
* **Mục đích học tập:** Giúp sinh viên hiểu rõ hơn về các thuật toán AI qua ví dụ trực quan.

---

## ✨ Tính năng chính

* Mô phỏng và giải khối Rubik **2x2x2** và **3x3x3**.
* Giao diện đồ họa **3D** trực quan bằng PyQt5 và PyOpenGL.
* Triển khai và so sánh các nhóm thuật toán:
    * **Tìm kiếm Mù (Uninformed Search):** BFS, DFS, UCS, IDS.
    * **Tìm kiếm Có thông tin (Informed Search):** Greedy Best-First, A*, IDA*.
    * **Tìm kiếm Cục bộ (Local Search):** Hill Climbing (Simple, Random Restart, Stochastic), Simulated Annealing, Genetic Algorithm, Local Beam Search.
    * **Tìm kiếm Đối nghịch & Trạng thái Tin cậy:** AND-OR Graph Search, Belief States.
    * **Bài toán Thỏa mãn Ràng buộc (CSP):** Backtracking, AC-3.
    * **Học Tăng cường (Reinforcement Learning):** Mô hình DeepCubeA (DQRN).
* Sử dụng **Pattern Databases (PDB)** cho hàm heuristic (ví dụ: góc của 2x2).
* Đánh giá hiệu năng chi tiết: thời gian, độ dài lời giải, số trạng thái duyệt/sinh ra, bộ nhớ, hệ số phân nhánh hiệu quả.

---

## 🚀 Công nghệ sử dụng

* **Ngôn ngữ:** Python 3.13
* **Giao diện & Đồ họa 3D:** PyQt5, PyOpenGL
* **Tính toán & AI:** NumPy, PyTorch (cho DeepCubeA)
* **Thư viện hỗ trợ:** `heapq`, `collections.deque`, `random`, `math`, `pickle`
* **Quản lý code:** Git & GitHub
* **IDE:** Visual Studio Code
* **Hệ điều hành:** Đa nền tảng (Windows, macOS)

---

## 📊 Đánh giá & Kết quả (Sơ lược)

Dự án thực hiện đánh giá thực nghiệm hiệu năng của các thuật toán trên cấu hình [Mô tả ngắn cấu hình máy tính nếu cần]. Các kết quả chi tiết về thời gian giải, số bước, bộ nhớ... được trình bày trong báo cáo đầy đủ.

*So sánh hiệu năng giữa các nhóm thuật toán.*
*Phân tích đặc điểm của từng thuật toán (ví dụ: A* vs IDA*, PDB vs DeepCubeA).*

**(Khuyến khích: Chèn ảnh GIF hoặc ảnh chụp màn hình giao diện phần mềm tại đây!)**
![Demo Screenshot/GIF](link_den_anh_gif_hoac_screenshot.png)

---

## 🛠️ Hướng dẫn cài đặt và sử dụng

1.  **Clone repository:**
    ```bash
    git clone [URL-GITHUB-CUA-BAN]
    cd [TEN-THU-MUC-REPO]
    ```
2.  **Cài đặt thư viện:** (Nên tạo môi trường ảo virtualenv/conda)
    ```bash
    pip install -r requirements.txt
    ```
    *(Lưu ý: Bạn cần tạo file `requirements.txt` liệt kê các thư viện như PyQt5, PyOpenGL, numpy, torch)*
3.  **Chạy ứng dụng:**
    ```bash
    python main.py
    ```
    *(Hoặc tên file Python chính của bạn)*

---

## 🔗 Link Báo Cáo Đầy Đủ & Mã Nguồn

* **Mã nguồn:** [Link đến GitHub Repo của bạn] (Thường là repo hiện tại)
* **Báo cáo chi tiết:** [Link đến file PDF báo cáo nếu có]

---

## 🚧 Hạn chế & Hướng phát triển

* **Hạn chế:**
    * Pattern Database mới chỉ ở mức cơ bản cho 2x2.
    * Huấn luyện mô hình DeepCubeA còn giới hạn (độ sâu 10) do hạn chế phần cứng.
* **Hướng phát triển:**
    * Mở rộng PDB cho 3x3 và các độ sâu lớn hơn.
    * Tối ưu và huấn luyện mô hình RL sâu hơn.
    * Thêm các kích thước Rubik khác (4x4x4,...).
    * Cải thiện hiệu năng đồ họa và giao diện người dùng.

---

*Chúc bạn có trải nghiệm thú vị với dự án!*