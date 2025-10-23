# src/map_generator/models/map_data.py

import json
import os
from typing import List, Tuple, Dict, Any

# Định nghĩa các kiểu dữ liệu tùy chỉnh để code dễ đọc hơn
Coord = Tuple[int, int, int]
Item = Dict[str, Any]
Obstacle = Dict[str, Any]

class MapData:
    """
    Lớp chứa toàn bộ dữ liệu cấu thành một map game hoàn chỉnh.
    Nó hoạt động như một cấu trúc dữ liệu chuẩn cho đầu ra của hệ thống sinh map.
    """
    def __init__(self,
                 grid_size: Tuple[int, int, int],
                 start_pos: Coord,
                 target_pos: Coord,
                 items: List[Item] = None,
                 obstacles: List[Obstacle] = None,
                 path_coords: List[Coord] = None,
                 map_type: str = 'unknown',
                 logic_type: str = 'unknown'):
        """
        Khởi tạo một đối tượng dữ liệu map.

        Args:
            grid_size (Tuple[int, int, int]): Kích thước của lưới (rộng, cao, sâu).
            start_pos (Coord): Tọa độ bắt đầu của người chơi.
            target_pos (Coord): Tọa độ đích của màn chơi.
            items (List[Item], optional): Danh sách các vật phẩm. Mặc định là None.
            obstacles (List[Obstacle], optional): Danh sách các chướng ngại vật. Mặc định là None.
            path_coords (List[Coord], optional): Danh sách tọa độ của các ô trên đường đi.
            map_type (str, optional): Tên của dạng map (topology) đã tạo ra nó.
            logic_type (str, optional): Tên của logic (placer) đã được áp dụng.
        """
        self.grid_size = grid_size
        self.start_pos = start_pos
        self.target_pos = target_pos
        
        # Xử lý an toàn cho các tham số mặc định là list để tránh lỗi
        self.items = items if items is not None else []
        self.path_coords = path_coords if path_coords is not None else []
        self.obstacles = obstacles if obstacles is not None else []
        
        # Metadata để dễ dàng truy vết và gỡ lỗi
        self.map_type = map_type
        self.logic_type = logic_type

    def to_dict(self) -> Dict[str, Any]:
        """
        Chuyển đổi đối tượng MapData thành một dictionary có cấu trúc rõ ràng.
        Cấu trúc này được thiết kế để game engine có thể dễ dàng đọc và phân tích.

        Returns:
            Dict[str, Any]: Một dictionary đại diện cho toàn bộ map.
        """
        return {
            "metadata": {
                "grid_size": self.grid_size,
                "map_type_source": self.map_type,
                "logic_type_source": self.logic_type
            },
            "player": {
                "start_position": self.start_pos
            },
            "world_objects": {
                "target_position": self.target_pos,
                "path_coords": self.path_coords,
                "items": self.items,
                "obstacles": self.obstacles
            }
        }

    def save_to_json(self, filepath: str):
        """

        Lưu dữ liệu map vào một file JSON tại đường dẫn được chỉ định.
        Tự động tạo thư mục nếu nó chưa tồn tại.

        Args:
            filepath (str): Đường dẫn đầy đủ đến file JSON đầu ra.
        """
        # Đảm bảo thư mục cha của file tồn tại
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                print(f"❌ Lỗi: Không thể tạo thư mục tại '{directory}'. Lỗi: {e}")
                return

        # Ghi file JSON với định dạng đẹp và hỗ trợ UTF-8
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
            
            print(f"✅ Map đã được lưu thành công tại: {filepath}")
        except IOError as e:
            print(f"❌ Lỗi: Không thể ghi file tại '{filepath}'. Lỗi: {e}")

    def to_game_engine_dict(self) -> Dict[str, Any]:
        """
        Chuyển đổi dữ liệu map từ định dạng "bản thiết kế" sang định dạng "game engine"
        dựa trên cấu trúc của map-config-template.json.

        Returns:
            Dict[str, Any]: Một dictionary có cấu trúc để game engine đọc.
        """
        # --- Hàm tiện ích ---
        def coord_to_obj(coord: Coord, y_offset: int = 0) -> Dict[str, int]:
            """Chuyển tuple (x,y,z) thành object {"x":x, "y":y, "z":z} và áp dụng offset y."""
            return {"x": coord[0], "y": coord[1] + y_offset, "z": coord[2]}

        # --- Bước 1: Tạo mặt đất (ground) ---
        # path_coords là "nguồn chân lý" cho toàn bộ các ô có thể đi được.
        # Bao gồm cả start_pos và target_pos nếu topology đã cung cấp đúng.
        potential_ground_coords = set(self.path_coords)
        # Thêm start và target để đảm bảo chúng luôn có ground bên dưới.
        potential_ground_coords.add(self.start_pos)
        potential_ground_coords.add(self.target_pos)

        # (CẢI TIẾN) Thêm tọa độ của tất cả các chướng ngại vật (wall, pit)
        # vào danh sách cần có ground để đảm bảo chúng có nền móng.
        for obs in self.obstacles:
            potential_ground_coords.add(tuple(obs['pos']))

        # --- (CẢI TIẾN) Xử lý trường hợp đặc biệt cho map maze ---
        if not self.path_coords and self.map_type == 'complex_maze_2d':
            print("    LOG: (Game Engine) Phát hiện map maze, dùng BFS để tìm các ô ground cần thiết...")
            
            # Tạo một set chứa tọa độ của tất cả các bức tường để tra cứu nhanh.
            wall_coords = {tuple(obs['pos']) for obs in self.obstacles if obs.get('type') == 'wall'}
            
            # Sử dụng thuật toán BFS để tìm tất cả các ô ground có thể đi được.
            # Hàng đợi (queue) cho BFS, bắt đầu từ vị trí của người chơi.
            queue = [self.start_pos]
            # Set để lưu các ô đã ghé thăm, tránh lặp vô hạn.
            visited_grounds = {self.start_pos}

            while queue:
                current_pos = queue.pop(0)
                
                # Khám phá 4 hướng xung quanh (trên mặt phẳng XZ)
                for dx, _, dz in [(1,0,0), (-1,0,0), (0,0,1), (0,0,-1)]:
                    next_pos = (current_pos[0] + dx, 0, current_pos[2] + dz)
                    
                    # Kiểm tra các điều kiện để một ô là hợp lệ:
                    # 1. Nằm trong biên của lưới.
                    # 2. Chưa được ghé thăm.
                    # 3. Không phải là một bức tường.
                    if (0 <= next_pos[0] < self.grid_size[0] and
                        0 <= next_pos[2] < self.grid_size[2] and
                        next_pos not in visited_grounds and
                        next_pos not in wall_coords):
                        visited_grounds.add(next_pos)
                        queue.append(next_pos)
            
            # Ground cuối cùng bao gồm các ô đi được và các ô nền móng của tường.
            final_ground_coords = visited_grounds.union(wall_coords)
        else:
            # Logic cũ cho các map có đường đi định trước
            final_ground_coords = potential_ground_coords
        
        game_blocks = [{"modelKey": "ground.normal", "position": coord_to_obj(pos)} for pos in sorted(list(final_ground_coords))]

        # --- Bước 2: Đặt các đối tượng lên trên mặt đất ---
        collectibles = []
        interactibles = []

        # Đặt vật phẩm (crystal, switch) với tọa độ y+1
        for i, item in enumerate(self.items):
            item_type = item.get('type')
            item_pos_on_ground = coord_to_obj(item['pos'], y_offset=1)
            
            if item_type in ['crystal', 'gem']: # [SỬA] Chấp nhận cả 'gem' và 'crystal'
                collectibles.append({
                    "id": f"c{i+1}",
                    "type": "crystal", # Luôn xuất ra là 'crystal' để game engine hiểu
                    "position": item_pos_on_ground
                })
            elif item_type == 'switch':
                interactibles.append({
                    "id": f"s{i+1}",
                    "type": item_type,
                    "position": item_pos_on_ground,
                    "initialState": item.get("initial_state", "off")
                })

        # [REFACTORED] Đặt chướng ngại vật với logic rõ ràng hơn
        for obs in self.obstacles:
            obs_type = obs.get('type')
            # Nếu chướng ngại vật đã có modelKey (ví dụ: tường từ mê cung), sử dụng nó.
            if 'modelKey' in obs:
                model_key = obs['modelKey']
            # Nếu không, gán modelKey mặc định dựa trên loại.
            elif obs_type == 'obstacle': # Vật cản có thể nhảy qua
                model_key = 'wall.brick01'
            else: # Các loại khác, mặc định là tường gạch
                model_key = 'wall.brick01'
            
            game_blocks.append({ "modelKey": model_key, "position": coord_to_obj(obs['pos'], y_offset=1) })

        # --- Bước 3: Hoàn thiện cấu trúc JSON ---
        return {
            "gameConfig": {
                "type": "maze",
                "renderer": "3d",
                "blocks": game_blocks,
                "players": [{
                    "id": "player1",
                    "start": {
                        **coord_to_obj(self.start_pos, y_offset=1),
                        "direction": 1 # Mặc định hướng về +X
                    }
                }],
                "collectibles": collectibles,
                "interactibles": interactibles,
                "finish": coord_to_obj(self.target_pos, y_offset=1)
            }
        }

    def save_to_game_engine_json(self, filepath: str):
        """Lưu dữ liệu map vào một file JSON theo định dạng của game engine."""
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_game_engine_dict(), f, indent=4, ensure_ascii=False)
            print(f"✅ Map (định dạng game) đã được lưu thành công tại: {filepath}")
        except IOError as e:
            print(f"❌ Lỗi: Không thể ghi file tại '{filepath}'. Lỗi: {e}")