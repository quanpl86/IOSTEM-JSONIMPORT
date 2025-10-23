# src/map_generator/topologies/interspersed_path.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord

class InterspersedPathTopology(BaseTopology):
    """
    Tạo ra một con đường thẳng đơn giản, đóng vai trò là "khung sườn"
    để lớp Placer có thể rải các vật phẩm và chướng ngại vật xen kẽ.
    
    Topology này được thiết kế để sử dụng cùng với các Placer dạy về logic
    điều kiện (If/Else) và vòng lặp không xác định (While).
    """
    
    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một con đường thẳng trên trục X hoặc Z.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về con đường thẳng này.
        """
        print("    LOG: Generating 'interspersed_path' topology...")
        
        # Lấy các tham số, nếu không có thì dùng giá trị mặc định.
        # Điều này giúp map linh hoạt hơn.
        path_length = params.get('path_length', 8)
        
        # Đảm bảo đường đi không quá dài so với map
        max_dim = max(grid_size[0], grid_size[2])
        if path_length >= max_dim - 2:
            path_length = max_dim - 3

        # Chọn trục ngẫu nhiên (X hoặc Z)
        axis = random.choice(['x', 'z'])
        
        # Tính toán vị trí bắt đầu an toàn để đường đi không bị ra ngoài biên
        if axis == 'x':
            start_x = random.randint(1, grid_size[0] - path_length - 2)
            start_z = random.randint(1, grid_size[2] - 2)
        else: # axis == 'z'
            start_x = random.randint(1, grid_size[0] - 2)
            start_z = random.randint(1, grid_size[2] - path_length - 2)
            
        start_pos: Coord = (start_x, 0, start_z)
        
        # Tạo ra danh sách các tọa độ trên đường đi
        path_coords: list[Coord] = []
        current_pos = list(start_pos)
        
        for _ in range(path_length):
            if axis == 'x':
                current_pos[0] += 1
            else: # axis == 'z'
                current_pos[2] += 1
            path_coords.append(tuple(current_pos))
            
        # Vị trí đích là điểm cuối cùng của đường đi
        target_pos = path_coords[-1]
        
        # Vị trí bắt đầu thực sự sẽ là một bước trước khi vào con đường chính
        # Điều này giúp Placer có thể đặt chướng ngại vật ngay ở ô đầu tiên
        # mà không lo trùng với vị trí của người chơi.
        if axis == 'x':
            actual_start_pos = (start_pos[0] - 1, start_pos[1], start_pos[2])
        else: # axis == 'z'
            actual_start_pos = (start_pos[0], start_pos[1], start_pos[2] - 1)


        return PathInfo(
            start_pos=actual_start_pos,
            target_pos=target_pos,
            path_coords=path_coords
        )