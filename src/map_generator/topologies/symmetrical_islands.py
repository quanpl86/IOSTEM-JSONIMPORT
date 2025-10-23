# src/map_generator/topologies/symmetrical_islands.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord

class SymmetricalIslandsTopology(BaseTopology):
    """
    Tạo ra các khu vực (đảo) có cấu trúc giống hệt nhau, được ngăn cách
    bởi các khoảng trống hoặc hành lang.
    
    Đây là dạng map lý tưởng để dạy về việc nhận biết mẫu lặp lại
    và phân rã vấn đề thành các hàm có thể tái sử dụng.
    """

    def _create_island_pattern(self, top_left_corner: Coord) -> list[Coord]:
        """
        Tạo ra một mẫu hình hòn đảo cụ thể.
        Hàm này có thể được thay đổi để tạo ra các mẫu phức tạp hơn.
        
        Args:
            top_left_corner (Coord): Tọa độ góc trên bên trái của hòn đảo.
            
        Returns:
            list[Coord]: Một danh sách các tọa độ tạo nên con đường trên đảo.
        """
        x, y, z = top_left_corner
        
        # Tạo một mẫu hình chữ U đơn giản
        # Path: (x,z) -> (x+1,z) -> (x+1,z+1) -> (x,z+1)
        p1 = (x, y, z)
        p2 = (x + 1, y, z)
        p3 = (x + 1, y, z + 1)
        p4 = (x, y, z + 1)
        
        return [p1, p2, p3, p4]

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một chuỗi các hòn đảo giống hệt nhau.

        Args:
            params (dict): Có thể chứa 'num_islands' để tùy chỉnh số lượng đảo.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về tất cả các hòn đảo.
        """
        print("    LOG: Generating 'symmetrical_islands' topology...")
        
        # --- (CẢI TIẾN) Đọc và ngẫu nhiên hóa số lượng đảo ---
        num_islands_param = params.get('num_islands', 2)
        if isinstance(num_islands_param, list) and len(num_islands_param) == 2:
            # Nếu num_islands là một khoảng [min, max], chọn ngẫu nhiên một giá trị
            num_islands = random.randint(num_islands_param[0], num_islands_param[1])
        else:
            # Nếu không, sử dụng giá trị được cung cấp hoặc mặc định
            num_islands = num_islands_param

        # --- (CẢI TIẾN) Tự động tính toán khoảng cách tối ưu giữa các đảo ---
        # Chiều rộng của mỗi hòn đảo là 2 (từ x đến x+1)
        island_width = 2
        # Tổng chiều rộng mà tất cả các đảo chiếm dụng
        total_islands_width = num_islands * island_width
        # Không gian còn lại trên lưới để phân bổ cho các cây cầu
        available_spacing = grid_size[0] - total_islands_width - 2 # Trừ 2 cho lề an toàn
        
        # Khoảng cách giữa các góc bắt đầu của hai đảo liên tiếp
        # Nếu chỉ có 1 đảo, spacing không có ý nghĩa.
        island_spacing = island_width + (available_spacing // (num_islands - 1)) if num_islands > 1 else 0

        # Tính toán vị trí bắt đầu an toàn
        start_x = 1
        start_z = random.randint(1, grid_size[2] - 4) # 4 là kích thước mẫu đảo
        y = 0
        
        start_pos: Coord = (start_x, y, start_z)
        
        all_path_coords: list[Coord] = []
        island_placement_coords: list[Coord] = [] # [SỬA] Danh sách riêng cho tọa độ của các đảo
        
        # Vòng lặp để tạo ra các hòn đảo
        for i in range(num_islands):
            # Tọa độ góc của mỗi hòn đảo được tính toán dựa trên khoảng cách
            island_corner = (start_x + i * island_spacing, y, start_z)
            
            # Tạo đường đi cho hòn đảo hiện tại
            island_path = self._create_island_pattern(island_corner)
            island_placement_coords.extend(island_path) # Thêm vào danh sách placement
            all_path_coords.extend(island_path)
            
            # Tạo "cây cầu" nối giữa các đảo (nếu không phải đảo cuối cùng)
            if i < num_islands - 1:
                # Điểm cuối của đảo hiện tại là island_path[-1] = (x, y, z+1)
                # Điểm đầu của đảo tiếp theo là (x + island_spacing, y, z)
                # Cầu sẽ nối từ (x, y, z+1) -> (x, y, z) -> ... -> (x + island_spacing, y, z)
                # Tuy nhiên, để đơn giản, ta sẽ tạo một cây cầu thẳng từ một điểm trên đảo này
                # đến điểm đầu của đảo tiếp theo.
                bridge_start = (island_corner[0] + 1, y, island_corner[2]) # Điểm (x+1, y, z)
                bridge_end = (start_x + (i + 1) * island_spacing, y, start_z) # Điểm đầu của đảo tiếp theo
                
                # (SỬA LỖI) Tạo cầu nối từ điểm sau bridge_start đến trước bridge_end
                for step in range(bridge_start[0] + 1, bridge_end[0]):
                    all_path_coords.append((step, y, start_z))

        target_pos = all_path_coords[-1]
        
        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=all_path_coords, # Chứa tất cả các điểm của các đảo và cầu
            placement_coords=island_placement_coords # [SỬA] Cung cấp tọa độ chỉ của các đảo
        )