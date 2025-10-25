# Hệ thống Sinh Map Tự động (Map Generation System)

Dự án này là một hệ thống mạnh mẽ được thiết kế để tự động hóa hoàn toàn quá trình tạo ra các màn chơi (game level) cho một trò chơi giáo dục lập trình. Hệ thống có khả năng sinh ra các màn chơi 3D phức tạp từ một file cấu hình đơn giản, bao gồm cả việc tạo lỗi trong code mẫu cho các thử thách gỡ lỗi (debugging).

## Mục tiêu

- **Tự động hóa**: Giảm thiểu công sức thủ công trong việc thiết kế và tạo màn chơi.
- **Dựa trên Curriculum**: Sinh map dựa trên một "chương trình học" được định nghĩa trước, đảm bảo các màn chơi phù hợp với mục tiêu sư phạm.
- **Đa dạng hóa**: Dễ dàng tạo ra nhiều biến thể (variant) cho cùng một yêu cầu màn chơi.
- **Tích hợp Solver**: Tự động tìm lời giải tối ưu cho mỗi màn chơi để xác định độ khó và cung cấp gợi ý. 
- **Tạo lỗi thông minh**: Tự động tạo ra các phiên bản code bị lỗi (sai tham số, sai thứ tự, thiếu lệnh...) cho các thử thách gỡ lỗi.

## Cấu trúc Thư mục

```
.
├── data/
│   ├── curriculum_source.xlsx  # File Excel nguồn để định nghĩa các màn chơi
│   ├── curriculum/             # Các file JSON được sinh ra từ file Excel
│   ├── base_maps/              # Các map cơ bản (chỉ cấu trúc) để gỡ lỗi
│   └── final_game_levels/      # Các file JSON màn chơi hoàn chỉnh để tích hợp vào game
├── src/
│   ├── map_generator/          # Module chính chịu trách nhiệm sinh cấu trúc map
│   └── bug_generator/          # Module chịu trách nhiệm tạo lỗi cho code mẫu
├── scripts/
│   ├── generate_curriculum.py  # Script chuyển đổi Excel -> JSON curriculum
│   ├── generate_all_maps.py    # Script chính điều phối toàn bộ quá trình sinh map
│   └── gameSolver.py           # Script tìm lời giải tối ưu cho một map
├── main.py                     # Điểm khởi chạy chính của toàn bộ hệ thống
├── requirements.txt            # Danh sách các thư viện Python cần thiết
└── README.md                   # File tài liệu này
```

## Luồng hoạt động (Workflow)

Hệ thống hoạt động theo một quy trình tự động từ đầu đến cuối:

1.  **Định nghĩa Curriculum**: Người thiết kế màn chơi (Level Designer) mở file `data/curriculum_source.xlsx` và thêm các dòng mới để định nghĩa các yêu cầu cho màn chơi (ví dụ: topic, độ khó, loại map, loại logic, loại lỗi cần tạo...).

2.  **Chạy Hệ thống**: Người dùng thực thi file `main.py`.

3.  **Sinh Curriculum JSON**: `main.py` gọi `scripts/generate_curriculum.py`. Script này đọc file Excel, phân tích cú pháp từng dòng và tạo ra các file `.json` tương ứng cho mỗi topic trong thư mục `data/curriculum/`.

4.  **Sinh Map Hoàn Chỉnh**: `main.py` tiếp tục gọi `scripts/generate_all_maps.py`. Script này thực hiện các bước sau cho mỗi yêu cầu trong file curriculum JSON:
    a.  **Sinh cấu trúc map**: Gọi `src/map_generator/service.py` để tạo cấu trúc vật lý của map (đất, tường, vật phẩm, người chơi...). Map cơ bản này được lưu vào `data/base_maps/` để kiểm tra.
    b.  **Tìm lời giải**: Gọi `scripts/gameSolver.py` để "chơi thử" map vừa tạo và tìm ra chuỗi hành động tối ưu (ví dụ: `['moveForward', 'turnLeft', 'collect']`). Solver cũng có khả năng tối ưu hóa chuỗi hành động này thành các cấu trúc phức tạp hơn như vòng lặp.
    c.  **Tạo code mẫu (Start Blocks)**:
        - **Đối với bài gỡ lỗi (Fixbug)**: Dựa vào `bug_type` được định nghĩa, hệ thống sẽ lấy lời giải đúng và gọi `src/bug_generator/service.py` để "làm hỏng" nó (ví dụ: thay đổi tham số trong vòng lặp, hoán đổi vị trí 2 khối lệnh).
        - **Đối với các bài học khác**: Hệ thống có thể cung cấp lời giải đã được tối ưu (có vòng lặp) hoặc một chuỗi lệnh thô để người chơi tự tối ưu.
    d.  **Tổng hợp và xuất file**: Tất cả thông tin (cấu trúc map, cấu hình Blockly, code mẫu, thông tin lời giải...) được tổng hợp lại và ghi ra một file JSON hoàn chỉnh trong thư mục `data/final_game_levels/`.

## Hướng dẫn sử dụng

### Yêu cầu

- Python 3.10 trở lên

### Cài đặt

1.  **Tạo và kích hoạt môi trường ảo:**

    *   Trên macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   Trên Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

2.  **Cài đặt các thư viện cần thiết:**

    ```bash
    pip install -r requirements.txt
    ```
    Các thư viện chính bao gồm:
    - `pandas`: Để đọc và xử lý file Excel.
    - `openpyxl`: Engine để `pandas` có thể làm việc với file `.xlsx`.
    - `numpy`: Thư viện nền tảng cho các tính toán khoa học, được `pandas` sử dụng.

### Chạy hệ thống

Để chạy toàn bộ quy trình (từ đọc Excel đến sinh map cuối cùng), chỉ cần thực thi file `main.py`:

```bash
python main.py
```

Hệ thống sẽ tự động thực hiện các bước và in ra log chi tiết trên terminal.

## Mở rộng hệ thống

Dự án được thiết kế với cấu trúc module hóa để dễ dàng mở rộng.

### Thêm một loại lỗi (Bug Type) mới

1.  Mở file `src/bug_generator/service.py`.
2.  Tạo một hàm private mới để xử lý logic tạo lỗi (ví dụ: `_introduce_duplicate_block_bug`). Hàm này có thể nhận đầu vào là một danh sách hành động (`List[str]`) hoặc một chuỗi XML (`str`).
3.  Đăng ký hàm mới này vào dictionary `BUG_GENERATORS` với một `bug_type` key mới.
4.  Cập nhật logic trong `scripts/generate_all_maps.py` để xử lý `bug_type` mới nếu cần (ví dụ: nếu loại lỗi mới yêu cầu xử lý trên XML thay vì list).
5.  Sử dụng `bug_type` key mới trong file `curriculum_source.xlsx`.

    **Lưu ý về các loại lỗi mới được đề xuất:**
    Để hỗ trợ đầy đủ các loại lỗi gỡ lỗi nâng cao, bạn cần mở rộng `src/bug_generator/service.py` để xử lý các `bug_type` sau:
    - `incorrect_control_structure_position`: Di chuyển một khối điều khiển (ví dụ: vòng lặp, điều kiện) đến vị trí sai.
    - `incorrect_loop_condition`: Thay đổi điều kiện của vòng lặp `while` (ví dụ: thêm/bỏ `NOT`).
    - `redundant_blocks`: Thêm các khối lệnh thừa vào chương trình.
    - `incorrect_logic_in_function`: Thay đổi logic bên trong một hàm (ví dụ: xóa một lệnh rẽ trong hàm `turnAround`).
    - `missing_block_in_function`: Xóa một khối lệnh cần thiết bên trong một hàm.
    - `missing_return_statement`: Xóa lệnh `return` trong một hàm có giá trị trả về.
    - `infinite_recursion`: Xóa điều kiện dừng của một hàm đệ quy.
    - `incorrect_parameter_handling`: Thay đổi cách một hàm sử dụng tham số của nó.
    - `missing_function_call`: Xóa một lệnh gọi hàm cần thiết từ chương trình chính.
    - `optimization_no_function`: Tạo code lặp lại thay vì sử dụng hàm để trừu tượng hóa.
    - `overly_complex_function`: Kết hợp nhiều hành động vào một hàm duy nhất khi nên chia nhỏ.

### Thêm một loại Map (Topology) mới

1.  Tạo một file Python mới trong `src/map_generator/topologies/`.
2.  Tạo một class mới trong file đó, kế thừa từ `BaseTopology`.
3.  Implement phương thức `create_map()` để định nghĩa logic tạo cấu trúc map.
4.  Đăng ký class mới này trong `src/map_generator/service.py`.