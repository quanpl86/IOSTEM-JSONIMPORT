# src/map_generator/placements/while_if_placer.py

import random
from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo

class WhileIfPlacer(BasePlacer):
    """
    Đặt các vật phẩm và chướng ngại vật một cách ngẫu nhiên để dạy về
    logic điều kiện (If/Else) và các vòng lặp không xác định (While).
    
    Placer này tạo ra các kịch bản mà người chơi không thể biết trước
    cấu trúc của map, buộc họ phải sử dụng cảm biến để đưa ra quyết định.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Nhận một con đường thẳng và rải các hố, vật phẩm, công tắc một cách
        ngẫu nhiên lên đó.

        Args:
            path_info (PathInfo): Thông tin đường đi từ một lớp Topology
                                  (thường là InterspersedPathTopology).
            params (dict): Các tham số bổ sung để điều chỉnh độ khó,
                           ví dụ: {'pit_chance': 0.3, 'item_chance': 0.4}.

        Returns:
            dict: Một dictionary chứa layout map hoàn chỉnh.
        """
        print(f"    LOG: Placing items with '{params.get('logic_type', 'while/if')}' logic...")

        # --- Lấy các tham số xác suất từ params để điều chỉnh độ khó ---
        # Nếu không có, sử dụng giá trị mặc định.
        pit_chance = params.get('pit_chance', 0.3)      # 30% cơ hội mỗi ô là hố
        item_chance = params.get('item_chance', 0.4)     # 40% cơ hội mỗi ô là vật phẩm
        switch_chance = params.get('switch_chance', 0.1) # 10% cơ hội mỗi ô là công tắc

        # --- Lấy danh sách các loại vật phẩm có thể xuất hiện từ params ---
        possible_items = params.get('possible_items', ['crystal'])

        items = []
        obstacles = []
        
        # --- Vòng lặp để "trang trí" con đường ---
        for pos in path_info.path_coords:
            # (SỬA LỖI) Bỏ qua ô cuối cùng là vị trí đích, không đặt gì ở đó.
            # Điều này đảm bảo đích đến luôn có thể tiếp cận và không bị che khuất.
            if pos == path_info.target_pos:
                continue

            rand_val = random.random() # Lấy một số ngẫu nhiên từ 0.0 đến 1.0

            # Các điều kiện này được sắp xếp để không bị chồng chéo
            if rand_val < pit_chance:
                # Nếu số ngẫu nhiên nhỏ hơn xác suất của hố (ví dụ: < 0.3)
                obstacles.append({"type": "pit", "pos": pos})
            elif rand_val < pit_chance + item_chance:
                # Nếu số ngẫu nhiên không phải là hố, nhưng nhỏ hơn tổng xác suất
                # của hố và vật phẩm (ví dụ: 0.3 <= rand_val < 0.7)
                
                # Chọn ngẫu nhiên một loại vật phẩm từ danh sách cho phép
                item_type = random.choice(possible_items)
                items.append({"type": item_type, "pos": pos})
            elif rand_val < pit_chance + item_chance + switch_chance:
                # Tương tự cho công tắc (ví dụ: 0.7 <= rand_val < 0.8)
                
                # Công tắc cũng là một loại "vật phẩm" có thể tương tác
                initial_state = random.choice(["on", "off"])
                items.append({"type": "switch", "pos": pos, "initial_state": initial_state})
            
            # Nếu rand_val lớn hơn tất cả các tổng xác suất (ví dụ: >= 0.8),
            # ô đó sẽ được để trống.

        return {
            "start_pos": path_info.start_pos,
            "target_pos": path_info.target_pos,
            "items": items,
            "obstacles": obstacles
        }