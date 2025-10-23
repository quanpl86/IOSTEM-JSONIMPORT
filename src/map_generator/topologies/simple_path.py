# src/map_generator/topologies/simple_path.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord

class SimplePathTopology(BaseTopology):
    """
    (Nâng cấp) Tạo ra một con đường ngắn cho các bài tập giới thiệu.
    Có khả năng tùy chỉnh độ dài và hình dạng qua params.
    """
    
    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        print(f"    LOG: Generating 'simple_path' with params: {params}")
        
        path_length = params.get('path_length', 3)
        pattern = params.get('pattern', 'straight')
        
        max_dim = min(grid_size[0], grid_size[2])
        if path_length >= max_dim - 3:
            path_length = max_dim - 4
        if path_length < 1:
            path_length = 1

        start_x = random.randint(1, grid_size[0] - path_length - 2)
        start_z = random.randint(1, grid_size[2] - path_length - 2)
        start_pos: Coord = (start_x, 0, start_z)
        
        path_coords: list[Coord] = []
        target_pos: Coord
        
        current_pos = list(start_pos)
        
        if pattern == 'straight':
            for _ in range(path_length):
                current_pos[0] += 1
                path_coords.append(tuple(current_pos))
            target_pos = (current_pos[0] + 1, current_pos[1], current_pos[2])

        elif pattern == 'corner':
            if path_length < 2:
                half_len, remaining_len = path_length, 0
            else:
                half_len = path_length // 2
                remaining_len = path_length - half_len
            
            for _ in range(half_len):
                current_pos[0] += 1
                path_coords.append(tuple(current_pos))
                
            for _ in range(remaining_len):
                current_pos[2] += 1
                path_coords.append(tuple(current_pos))
                
            target_pos = (current_pos[0], current_pos[1], current_pos[2] + 1)
        else:
             for _ in range(path_length):
                current_pos[0] += 1
                path_coords.append(tuple(current_pos))
             target_pos = (current_pos[0] + 1, current_pos[1], current_pos[2])

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=path_coords
        )