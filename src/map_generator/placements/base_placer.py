# src/map_generator/placements/base_placer.py

# 'abc' là viết tắt của Abstract Base Classes (Lớp cơ sở trừu tượng).
from abc import ABC, abstractmethod
# Sử dụng typing để định nghĩa các kiểu dữ liệu một cách rõ ràng.
from typing import Dict, Any

# Import lớp PathInfo để sử dụng trong type hinting, đảm bảo tính nhất quán
# về dữ liệu đầu vào cho tất cả các lớp Placer.
from src.map_generator.models.path_info import PathInfo

class BasePlacer(ABC):
    """
    Lớp cơ sở trừu tượng (Interface) cho tất cả các chiến lược đặt vật phẩm và logic game.
    
    Mỗi lớp con kế thừa từ BasePlacer BẮT BUỘC phải hiện thực hóa
    phương thức place_items(). Nếu không, Python sẽ báo lỗi khi
    khởi tạo đối tượng của lớp con đó.
    """

    @abstractmethod
    def place_items(self, path_info: PathInfo, params: dict) -> Dict[str, Any]:
        """
        Phương thức cốt lõi để nhận một đường đi "thô" và đặt các vật phẩm,
        chướng ngại vật, và các logic game khác lên đó.

        Args:
            path_info (PathInfo): Một đối tượng chứa thông tin đường đi đã được
                                  tạo bởi một lớp Topology.
            params (dict): Một dictionary chứa các tham số bổ sung để tùy chỉnh
                           việc đặt logic (ví dụ: {'difficulty': 'hard'}).

        Returns:
            Dict[str, Any]: Một dictionary chứa layout map hoàn chỉnh, sẵn sàng
                            để được đóng gói vào một đối tượng MapData.
                            Cấu trúc mong đợi:
                            {
                                "start_pos": (x, y, z),
                                "target_pos": (tx, ty, tz),
                                "items": [{"type": "crystal", "pos": (x1, y1, z1)}, ...],
                                "obstacles": [{"type": "pit", "pos": (x2, y2, z2)}, ...]
                            }
        """
        # Phương thức này không có code bên trong.
        # Nó chỉ định nghĩa "chữ ký" mà các lớp con phải tuân theo.
        pass