# src/map_generator/placements/algorithm_placer.py

from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo
from src.utils.randomizer import shuffle_list
import random

class AlgorithmPlacer(BasePlacer):
    """
    Đặt các đối tượng cho các bài toán thuật toán phức tạp.
    
    Placer này hoạt động với các Topology như ComplexMaze, nơi không có
    đường đi định trước. Nó chỉ đặt mục tiêu ở một vị trí khó,
    buộc người chơi phải tự thiết kế thuật toán để tìm ra nó.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Nhận một map mê cung và đặt các vật phẩm vào các vị trí chiến lược
        (ví dụ: ngõ cụt) để tạo ra thử thách tìm kiếm.

        Args:
            path_info (PathInfo): Thông tin từ ComplexMazeTopology, chủ yếu
                                  chứa chướng ngại vật (tường).
            params (dict): Có thể chứa 'items_to_place'.

        Returns:
            dict: Một dictionary chứa layout map hoàn chỉnh.
        """
        print("    LOG: Placing items with 'algorithm' logic...")
        
        items_to_place = params.get('items_to_place', [])
        items = []
        obstacles = path_info.obstacles
        
        # [SỬA LỖI] Xử lý hai trường hợp:
        # 1. Có chướng ngại vật (dành cho map mê cung): Tìm ngõ cụt để đặt.
        # 2. Không có chướng ngại vật (dành cho map đường thẳng): Đặt ngẫu nhiên trên đường đi.
        if items_to_place and obstacles:
            # --- Tìm các vị trí có thể đặt vật phẩm (ngõ cụt) ---
            wall_coords = {obs['pos'] for obs in obstacles}
            possible_placements = []
            
            # Chỉ chạy logic này nếu có tường, tránh lỗi max() trên list rỗng
            if wall_coords:
                # Duyệt qua các ô không phải là tường
                grid_width = max(c[0] for c in wall_coords) + 1
                grid_depth = max(c[2] for c in wall_coords) + 1
    
                for x in range(1, grid_width, 2):
                    for z in range(1, grid_depth, 2):
                        pos = (x, 0, z)
                        if pos not in wall_coords and pos != path_info.start_pos and pos != path_info.target_pos:
                            # Đếm số lượng tường xung quanh
                            neighbor_walls = 0
                            for dx, _, dz in [(1,0,0), (-1,0,0), (0,0,1), (0,0,-1)]:
                                if (pos[0] + dx, 0, pos[2] + dz) in wall_coords:
                                    neighbor_walls += 1
                            # Nếu có 3 bức tường xung quanh, đó là ngõ cụt
                            if neighbor_walls == 3:
                                possible_placements.append(pos)
                
                # Xáo trộn các vị trí và đặt vật phẩm
                shuffled_placements = shuffle_list(possible_placements)
                for item_type in items_to_place:
                    if shuffled_placements:
                        item_pos = shuffled_placements.pop()
                        items.append({"type": item_type, "pos": item_pos})
        elif items_to_place and not obstacles:
            # Logic dự phòng: Nếu không có tường, đặt vật phẩm ngẫu nhiên trên đường đi
            print("    LOG: (AlgorithmPlacer) No obstacles found. Placing items randomly on path.")
            available_slots = shuffle_list([p for p in path_info.path_coords if p != path_info.start_pos and p != path_info.target_pos])
            for item_type in items_to_place:
                if available_slots:
                    pos = available_slots.pop()
                    items.append({"type": item_type, "pos": pos})

        return {
            "start_pos": path_info.start_pos,
            "target_pos": path_info.target_pos,
            "items": items,
            "obstacles": obstacles
        }