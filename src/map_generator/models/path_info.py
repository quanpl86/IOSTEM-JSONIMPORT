# src/map_generator/models/path_info.py

# Sử dụng dataclasses để tạo các lớp dữ liệu một cách ngắn gọn và mạnh mẽ.
from dataclasses import dataclass, field
# Sử dụng typing để định nghĩa các kiểu dữ liệu một cách rõ ràng.
from typing import List, Tuple, Dict, Any

# --- Định nghĩa các kiểu dữ liệu tùy chỉnh (Type Aliases) ---
# Việc này giúp code ở những nơi khác trở nên dễ đọc hơn.
# Thay vì viết Tuple[int, int, int] ở nhiều nơi, ta chỉ cần viết Coord.
Coord = Tuple[int, int, int]
Obstacle = Dict[str, Any]


@dataclass
class PathInfo:
    """
    Một lớp dữ liệu để chứa thông tin "thô" về một con đường
    được tạo ra bởi một chiến lược Topology.
    
    Nó đóng vai trò là một hợp đồng chuẩn để truyền dữ liệu 
    giữa các lớp Topology và các lớp Placer.
    """
    # Tọa độ bắt đầu của con đường, nơi nhân vật sẽ xuất hiện.
    start_pos: Coord
    
    # Tọa độ kết thúc của con đường, nơi đích sẽ được đặt.
    target_pos: Coord
    
    # Một danh sách các tọa độ tạo nên con đường chính.
    # Các lớp Placer sẽ sử dụng danh sách này để quyết định vị trí đặt vật phẩm.
    path_coords: List[Coord]
    
    # (CẢI TIẾN) Một danh sách các tọa độ đặc biệt dành cho việc đặt đối tượng.
    # Nếu danh sách này rỗng, Placer sẽ mặc định sử dụng path_coords.
    # Điều này giúp tách biệt "đường đi" và "điểm đặt vật phẩm".
    placement_coords: List[Coord] = field(default_factory=list)
    
    # Một số Topology (như mê cung) có thể tạo ra chướng ngại vật (tường) trực tiếp.
    # Placer có thể sử dụng hoặc thêm vào danh sách này.
    # 'default_factory=list' là cách an toàn để đảm bảo mỗi đối tượng PathInfo mới
    # sẽ có một danh sách trống riêng, tránh các lỗi chia sẻ dữ liệu không mong muốn.
    obstacles: List[Obstacle] = field(default_factory=list)

    def __post_init__(self):
        """
        Phương thức này được tự động gọi sau khi __init__ hoàn thành.
        Chúng ta có thể dùng nó để kiểm tra tính hợp lệ của dữ liệu.
        """
        if not isinstance(self.start_pos, tuple) or len(self.start_pos) != 3:
            raise TypeError("start_pos phải là một tuple (x, y, z)")
        if not isinstance(self.target_pos, tuple) or len(self.target_pos) != 3:
            raise TypeError("target_pos phải là một tuple (x, y, z)")
        if not isinstance(self.path_coords, list):
            raise TypeError("path_coords phải là một list các tọa độ")

    def get_path_length(self) -> int:
        """Một phương thức tiện ích ví dụ để tính chiều dài của đường đi."""
        return len(self.path_coords)