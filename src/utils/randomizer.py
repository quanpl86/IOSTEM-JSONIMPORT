# src/utils/randomizer.py

import random
from typing import Tuple, List, Any

# Import các kiểu dữ liệu và hằng số từ geometry để sử dụng
from .geometry import Vector3, DIRECTIONS_2D

def get_safe_start_position(grid_size: Tuple[int, int, int], 
                                margin: int = 1, 
                                on_floor: bool = True) -> Vector3:
    """
    Lấy một tọa độ bắt đầu ngẫu nhiên nằm trong một vùng an toàn,
    cách các cạnh của map một khoảng 'margin'.

    Args:
        grid_size (Tuple[int, int, int]): Kích thước của lưới.
        margin (int, optional): Khoảng cách tối thiểu từ các cạnh. Mặc định là 1.
        on_floor (bool, optional): Nếu True, tọa độ Y sẽ luôn là 0. Mặc định là True.

    Returns:
        Vector3: Một tọa độ (x, y, z) ngẫu nhiên và an toàn.
    """
    safe_min_x = margin
    safe_max_x = grid_size[0] - 1 - margin
    
    safe_min_z = margin
    safe_max_z = grid_size[2] - 1 - margin

    x = random.randint(safe_min_x, safe_max_x)
    z = random.randint(safe_min_z, safe_max_z)
    
    if on_floor:
        y = 0
    else:
        safe_min_y = margin
        safe_max_y = grid_size[1] - 1 - margin
        y = random.randint(safe_min_y, safe_max_y)

    return (x, y, z)

def get_random_2d_direction() -> Vector3:
    """
    Chọn một vector chỉ hướng ngẫu nhiên trên mặt phẳng XZ.

    Returns:
        Vector3: Một trong các vector (1,0,0), (-1,0,0), (0,0,1), (0,0,-1).
    """
    return random.choice(DIRECTIONS_2D)

def shuffle_list(input_list: List[Any]) -> List[Any]:
    """
    Xáo trộn một danh sách và trả về một bản sao đã xáo trộn.
    Hàm này an toàn hơn 'random.shuffle' vì nó không thay đổi danh sách gốc.

    Args:
        input_list (List[Any]): Danh sách đầu vào.

    Returns:
        List[Any]: Một danh sách mới với các phần tử đã được xáo trộn.
    """
    shuffled = input_list[:]  # Tạo một bản sao của danh sách
    random.shuffle(shuffled)
    return shuffled

def chance(probability: float) -> bool:
    """
    Trả về True với một xác suất cho trước.

    Args:
        probability (float): Một số từ 0.0 (luôn False) đến 1.0 (luôn True).

    Returns:
        bool: True hoặc False, dựa trên xác suất.
        
    Example:
        if chance(0.3): # Có 30% cơ hội để đoạn code này chạy
            print("You got lucky!")
    """
    if not 0.0 <= probability <= 1.0:
        raise ValueError("Xác suất phải nằm trong khoảng từ 0.0 đến 1.0")
    return random.random() < probability