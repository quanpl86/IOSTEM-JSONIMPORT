# src/map_generator/topologies/spiral.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord

class SpiralTopology(BaseTopology):
    """
    Tạo ra một con đường xoắn ốc hình chữ nhật đi vào trung tâm.
    Độ dài của các cạnh sẽ giảm dần, tạo ra một bài toán lý tưởng
    để thực hành sử dụng biến trong vòng lặp.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một đường đi xoắn ốc.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về con đường xoắn ốc.
        """
        print("    LOG: Generating 'spiral' topology...")

        # Xác định giới hạn của xoắn ốc để nó nằm gọn trong map
        # Chúng ta chừa một lề 1 ô xung quanh
        min_x, max_x = 1, grid_size[0] - 2
        min_z, max_z = 1, grid_size[2] - 2
        
        y = 0
        start_pos: Coord = (min_x, y, min_z)
        
        path_coords: list[Coord] = []
        
        # Bắt đầu vẽ từ điểm bắt đầu
        current_x, current_z = min_x, min_z

        while min_x < max_x and min_z < max_z:
            # 1. Vẽ cạnh phải ->
            for x in range(min_x, max_x):
                current_x += 1
                path_coords.append((current_x, y, current_z))
            min_z += 1 # Thu hẹp biên trên

            # 2. Vẽ cạnh dưới v
            for z in range(min_z, max_z):
                current_z += 1
                path_coords.append((current_x, y, current_z))
            max_x -= 1 # Thu hẹp biên phải

            # Kiểm tra để tránh vẽ chồng lên nhau nếu xoắn ốc đã kết thúc
            if not (min_x < max_x and min_z < max_z):
                break

            # 3. Vẽ cạnh trái <-
            for x in range(max_x, min_x, -1):
                current_x -= 1
                path_coords.append((current_x, y, current_z))
            max_z -= 1 # Thu hẹp biên dưới

            # 4. Vẽ cạnh trên ^
            for z in range(max_z, min_z, -1):
                current_z -= 1
                path_coords.append((current_x, y, current_z))
            min_x += 1 # Thu hẹp biên trái

        # Vị trí đích là điểm cuối cùng của đường đi
        target_pos = path_coords[-1] if path_coords else start_pos

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=path_coords
        )