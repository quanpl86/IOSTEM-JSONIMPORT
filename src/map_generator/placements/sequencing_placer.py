# src/map_generator/placements/sequencing_placer.py

from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo
from src.utils.randomizer import shuffle_list
import random

class SequencingPlacer(BasePlacer):
    """
    (Nâng cấp) Đặt các đối tượng cho thử thách tuần tự.
    Có khả năng đặt nhiều loại và số lượng đối tượng khác nhau dựa vào params.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        print("    LOG: Placing items with 'sequencing' logic (UPGRADED)...")

        # --- Đọc các tham số chi tiết từ params ---
        # `items_to_place` sẽ là một danh sách các loại vật phẩm cần đặt
        # Ví dụ: ["crystal", "crystal", "switch"]
        items_to_place_param = params.get('items_to_place', ["crystal"])
        # [SỬA LỖI] Đảm bảo items_to_place luôn là một list.
        # Một số curriculum có thể định nghĩa nó là một string đơn lẻ (ví dụ: "crystal").
        items_to_place = items_to_place_param if isinstance(items_to_place_param, list) else [items_to_place_param]
        
        # `obstacles_to_place` là danh sách các loại chướng ngại vật
        # Ví dụ: ["pit", "pit"]
        obstacles_to_place_param = params.get('obstacles_to_place', [])
        # [SỬA LỖI] Tương tự, đảm bảo obstacles_to_place cũng là một list.
        obstacles_to_place = obstacles_to_place_param if isinstance(obstacles_to_place_param, list) else [obstacles_to_place_param]

        # Lấy tất cả các vị trí có thể đặt đối tượng và xáo trộn chúng
        available_slots = shuffle_list(path_info.path_coords)

        # Kiểm tra để đảm bảo có đủ chỗ
        total_objects = len(items_to_place) + len(obstacles_to_place)
        if len(available_slots) < total_objects:
            print(f"   ⚠️ Cảnh báo: Đường đi không đủ dài để đặt {total_objects} đối tượng.")
            # Cắt bớt danh sách nếu không đủ chỗ
            while len(available_slots) < len(items_to_place) + len(obstacles_to_place):
                if obstacles_to_place:
                    obstacles_to_place.pop()
                elif items_to_place:
                    items_to_place.pop()

        items = []
        obstacles = []
        
        # Đặt chướng ngại vật
        for obs_type in obstacles_to_place:
            if available_slots:
                pos = available_slots.pop()
                obstacles.append({"type": obs_type, "pos": pos})
        
        # Đặt vật phẩm
        for item_type in items_to_place:
            if available_slots:
                pos = available_slots.pop()
                # Xử lý các trường hợp đặc biệt như 'switch'
                if item_type == "switch":
                    initial_state = random.choice(["on", "off"])
                    items.append({"type": item_type, "pos": pos, "initial_state": initial_state})
                else:
                    items.append({"type": item_type, "pos": pos})

        return {
            "start_pos": path_info.start_pos,
            "target_pos": path_info.target_pos,
            "items": items,
            "obstacles": obstacles
        }