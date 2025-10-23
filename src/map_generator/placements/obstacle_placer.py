# src/map_generator/placements/obstacle_placer.py

import random
from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo

class ObstaclePlacer(BasePlacer):
    """
    Placer chuyên để đặt các chướng ngại vật (tường) lên đường đi,
    yêu cầu người chơi phải sử dụng lệnh 'jump'.
    Có thể kết hợp đặt thêm các vật phẩm và công tắc.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Đặt các vật phẩm, công tắc và quan trọng nhất là các chướng ngại vật.

        Args:
            path_info (PathInfo): Thông tin đường đi từ Topology.
            params (dict): Các tham số điều khiển việc đặt đối tượng.
                - obstacles (int): Số lượng vật cản cần đặt.
                - items_to_place (list): Danh sách các loại vật phẩm cần đặt (vd: ["crystal", "switch"]).

        Returns:
            dict: Layout map hoàn chỉnh.
        """
        print("    LOG: Placing items and obstacles with 'obstacle' logic...")

        items = []
        obstacles = []
        
        # Lấy danh sách các tọa độ có thể đặt đối tượng, loại trừ điểm bắt đầu và kết thúc
        possible_coords = [p for p in path_info.path_coords if p != path_info.start_pos and p != path_info.target_pos]
        random.shuffle(possible_coords)

        # 1. Đặt chướng ngại vật (ưu tiên)
        num_obstacles = params.get('obstacles', 0)
        for _ in range(min(num_obstacles, len(possible_coords))):
            pos = possible_coords.pop(0)
            obstacles.append({"type": "wall", "pos": pos})

        # 2. [MỞ RỘNG] Đặt các vật phẩm và công tắc khác vào các vị trí còn lại
        items_to_place = params.get('items_to_place', [])
        for item_type in items_to_place:
            if not possible_coords:
                print(f"    ⚠️ Cảnh báo: Không còn vị trí trống để đặt '{item_type}'.")
                break
            pos = possible_coords.pop(0)
            items.append({"type": item_type, "pos": pos})

        return {
            "start_pos": path_info.start_pos,
            "target_pos": path_info.target_pos,
            "items": items,
            "obstacles": obstacles
        }
