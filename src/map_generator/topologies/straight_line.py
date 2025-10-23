# src/map_generator/topologies/straight_line.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord

# --- ĐẢM BẢO TÊN LỚP NÀY HOÀN TOÀN CHÍNH XÁC ---
class StraightLineTopology(BaseTopology):
    """
    Tạo ra một con đường thẳng dài trên một trục.
    
    Đây là một topology đa năng, được sử dụng cho nhiều chủ đề khác nhau
    như Vòng lặp For, Biến, và Vòng lặp While.
    """
    
    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một đường thẳng với chiều dài và hướng ngẫu nhiên.

        Args:
            params (dict): Có thể chứa 'path_length' để tùy chỉnh chiều dài.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về đường thẳng.
                      'path_coords' sẽ chứa tọa độ của các ô trên đường đi.
        """
        print("    LOG: Generating 'straight_line' topology...")
        
        # --- (CẢI TIẾN) Đọc và ngẫu nhiên hóa chiều dài đường đi ---
        path_length_param = params.get('path_length', [5, 8])
        if isinstance(path_length_param, list) and len(path_length_param) == 2:
            # Nếu path_length là một khoảng [min, max], chọn ngẫu nhiên một giá trị
            path_length = random.randint(path_length_param[0], path_length_param[1])
        else:
            # Nếu không, sử dụng giá trị được cung cấp
            path_length = int(path_length_param)

        # Đảm bảo đường đi không quá dài so với map
        max_dim = max(grid_size[0], grid_size[2])
        if path_length >= max_dim - 2:
            path_length = max_dim - 3

        # Chọn một trục (X hoặc Z) và hướng (tiến hoặc lùi) ngẫu nhiên
        axis = random.choice(['x', 'z'])
        direction = random.choice([1, -1])
        
        # Tính toán vị trí bắt đầu an toàn
        total_cells_needed = path_length + 2
        
        y = 0
        start_pos_list = [0, y, 0]
        
        if axis == 'x':
            if direction == 1:
                start_x = random.randint(0, grid_size[0] - total_cells_needed)
            else:
                start_x = random.randint(total_cells_needed - 1, grid_size[0] - 1)
            start_pos_list[0] = start_x
            start_pos_list[2] = random.randint(0, grid_size[2] - 1)
        else: # axis == 'z'
            if direction == 1:
                start_z = random.randint(0, grid_size[2] - total_cells_needed)
            else:
                start_z = random.randint(total_cells_needed - 1, grid_size[2] - 1)
            start_pos_list[2] = start_z
            start_pos_list[0] = random.randint(0, grid_size[0] - 1)
        
        start_pos: Coord = tuple(start_pos_list)
        
        # Tạo ra danh sách các tọa độ trên đường đi
        path_coords: list[Coord] = []
        current_pos = list(start_pos)
        
        for _ in range(path_length):
            if axis == 'x':
                current_pos[0] += direction
            else:
                current_pos[2] += direction
            path_coords.append(tuple(current_pos))
        
        # Vị trí đích
        if axis == 'x':
            current_pos[0] += direction
        else:
            current_pos[2] += direction
        target_pos = tuple(current_pos)
        
        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=path_coords
        )