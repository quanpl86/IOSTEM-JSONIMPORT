# src/map_generator/topologies/square.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, FORWARD_Z, BACKWARD_X, BACKWARD_Z

class SquareTopology(BaseTopology):
    """
    Tạo ra một con đường hình vuông.
    
    Đây là dạng map kinh điển để dạy về việc lặp lại một chuỗi hành động
    (ví dụ: đi thẳng một đoạn rồi rẽ). Nó sử dụng logic "vòng lặp mở",
    nghĩa là điểm bắt đầu và kết thúc nằm bên ngoài hình vuông.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một hình vuông với kích thước và vị trí ngẫu nhiên.

        Args:
            params (dict): Có thể chứa 'side_length' để tùy chỉnh kích thước.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về hình vuông. 
                      'path_coords' sẽ chứa tọa độ của 4 góc.
        """
        print("    LOG: Generating 'square_shape' topology...")
        
        # Lấy kích thước cạnh, mặc định là 5. side_length là số bước đi.
        # (CẢI TIẾN) Đọc và ngẫu nhiên hóa kích thước cạnh từ params
        side_length_param = params.get('side_length', [4, 6]) # Mặc định là một khoảng
        if isinstance(side_length_param, list) and len(side_length_param) == 2:
            # Nếu side_length là một khoảng [min, max], chọn ngẫu nhiên một giá trị
            side_length = random.randint(side_length_param[0], side_length_param[1])
        else:
            # Nếu không, sử dụng giá trị được cung cấp
            side_length = int(side_length_param)

        # Đảm bảo hình vuông nằm gọn trong map với một lề an toàn
        # Cần side_length + 1 ô cho các góc, và thêm 1 ô cho start/target
        max_size = min(grid_size[0], grid_size[2]) - 2
        if side_length > max_size:
            side_length = max_size
        if side_length < 2: side_length = 2 # Đảm bảo kích thước tối thiểu
            
        start_x = random.randint(1, grid_size[0] - side_length - 2)
        start_z = random.randint(1, grid_size[2] - side_length - 2)
        y = 0

        # --- Xác định vị trí bắt đầu và kết thúc theo logic "vòng lặp mở" ---
        # Người chơi bắt đầu ở một ô bên trái, đi vào góc C1.
        start_pos: Coord = (start_x - 1, y, start_z)
        target_pos: Coord = (start_x - 1, y, start_z + side_length)

        # --- (SỬA LỖI) Tạo ra path_coords và placement_coords đầy đủ ---
        path_coords: list[Coord] = []
        
        # Điểm bắt đầu và kết thúc cũng là một phần của đường đi
        path_coords.append(start_pos)

        # Tạo đường đi đầy đủ cho 4 cạnh
        current_pos = (start_x, y, start_z)
        path_coords.append(current_pos)
        c1 = current_pos
        for _ in range(side_length):
            current_pos = add_vectors(current_pos, FORWARD_X)
            path_coords.append(current_pos)
        c2 = current_pos
        for _ in range(side_length):
            current_pos = add_vectors(current_pos, FORWARD_Z)
            path_coords.append(current_pos)
        c3 = current_pos
        for _ in range(side_length):
            current_pos = add_vectors(current_pos, BACKWARD_X)
            path_coords.append(current_pos)
        c4 = current_pos
        
        # Thêm đường đi ra target
        path_coords.append(target_pos)

        # placement_coords chỉ chứa 4 góc để Placer đặt vật phẩm
        placement_coords = [c1, c2, c3, c4]

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=list(dict.fromkeys(path_coords)), # Loại bỏ các điểm trùng lặp
            placement_coords=placement_coords
        )