# src/map_generator/topologies/plowing_field.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord

class PlowingFieldTopology(BaseTopology):
    """
    Tạo ra một con đường đi theo kiểu "luống cày" (zig-zag qua lại)
    để lấp đầy một khu vực hình chữ nhật.
    
    Đây là dạng map kinh điển để dạy về vòng lặp lồng nhau.
    """
    
    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một đường đi zig-zag qua các hàng và cột.

        Args:
            params (dict): Cần chứa 'rows' và 'cols' để xác định kích thước cánh đồng.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về đường đi luống cày.
        """
        print("    LOG: Generating 'plowing_field' topology...")
        
        # --- (CẢI TIẾN) Đọc và ngẫu nhiên hóa kích thước của "cánh đồng" ---
        rows_param = params.get('rows', [3, 4])
        cols_param = params.get('cols', [4, 6])

        rows = random.randint(*rows_param) if isinstance(rows_param, list) else rows_param
        cols = random.randint(*cols_param) if isinstance(cols_param, list) else cols_param

        # Đảm bảo khu vực này nằm gọn trong map
        max_width = grid_size[0] - 2
        max_depth = grid_size[2] - 2
        
        # Điều chỉnh lại kích thước nếu nó vượt quá giới hạn của lưới
        # cols là số ô trên một hàng, không phải số bước đi
        # Một hàng có 'cols' ô sẽ chiếm 'cols' đơn vị chiều rộng.
        if cols >= max_width:
            cols = max_width
        if rows >= max_depth:
            rows = max_depth

        # Tính toán vị trí bắt đầu an toàn
        start_x = random.randint(1, grid_size[0] - cols - 2)
        start_z = random.randint(1, grid_size[2] - rows - 2)
        y = 0

        # Vị trí bắt đầu của người chơi sẽ là một bước trước khi vào "cánh đồng"
        start_pos: Coord = (start_x - 1, y, start_z)
        
        # Tạo đường đi dạng zig-zag qua lại
        path_coords: list[Coord] = []
        
        # Thiết lập vị trí bắt đầu của con trỏ "cày"
        current_x, current_y, current_z = start_x, y, start_z
        
        # Hướng di chuyển ban đầu (1: đi theo chiều dương X, -1: đi theo chiều âm X)
        direction = 1 

        # Vòng lặp ngoài: lặp qua từng hàng (row)
        for r in range(rows):
            # Thêm ô đầu tiên của hàng vào đường đi
            path_coords.append((current_x, current_y, current_z))

            # Vòng lặp trong: lặp qua từng cột (col) để đi hết một hàng
            # Đi 'cols - 1' bước để tạo ra một hàng có 'cols' ô
            for _ in range(cols - 1):
                current_x += direction
                path_coords.append((current_x, current_y, current_z))
            
            # Chuyển sang hàng tiếp theo (nếu chưa phải hàng cuối)
            if r < rows - 1:
                current_z += 1
                path_coords.append((current_x, current_y, current_z)) # Thêm ô để rẽ
                direction *= -1 # Đảo chiều di chuyển cho hàng tiếp theo

        target_pos = path_coords[-1]

        return PathInfo(start_pos=start_pos, target_pos=target_pos, path_coords=path_coords)