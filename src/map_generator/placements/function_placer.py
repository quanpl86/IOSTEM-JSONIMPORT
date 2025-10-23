# src/map_generator/placements/function_placer.py

from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo

class FunctionPlacer(BasePlacer):
    """
    Đặt các vật phẩm để khuyến khích người chơi sử dụng Hàm và Tham số.
    
    Placer này hoạt động bằng cách đặt vật phẩm lên các mẫu hình (patterns)
    mà Topology đã tạo ra, làm cho sự lặp lại của các mẫu hình đó trở nên
    rõ ràng và trực quan.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Nhận một con đường có các mẫu hình lặp lại và đặt vật phẩm lên đó.

        Args:
            path_info (PathInfo): Thông tin đường đi từ một lớp Topology
                                  (ví dụ: SymmetricalIslandsTopology).
            params (dict): Các tham số bổ sung.

        Returns:
            dict: Một dictionary chứa layout map hoàn chỉnh.
        """
        print("    LOG: Placing items with 'function' or 'parameter' logic...")

        # Giống như ForLoopPlacer, logic cốt lõi rất đơn giản:
        # Topology đã làm hết phần việc khó là tính toán các tọa độ của
        # các mẫu hình lặp lại. Placer này chỉ cần đặt vật phẩm lên
        # tất cả các điểm đó.
        
        # (CẢI TIẾN) Sử dụng placement_coords để chỉ đặt vật phẩm lên các "hòn đảo",
        # bỏ qua "cây cầu", làm nổi bật mẫu hình cần nhận biết.
        coords_to_place_on = path_info.placement_coords if path_info.placement_coords else path_info.path_coords

        # (SỬA LỖI) Đặt vật phẩm lên tất cả các điểm, TRỪ điểm cuối cùng là đích đến.
        # Điều này tránh việc vật phẩm và đích bị đặt chồng lên nhau.
        items = [{"type": "crystal", "pos": pos} for pos in coords_to_place_on if pos != path_info.target_pos]

        # Tương tự ForLoop, chúng ta tránh chướng ngại vật để không làm
        # người chơi phân tâm khỏi mục tiêu chính là nhận biết mẫu hình.
        obstacles = []

        return {
            "start_pos": path_info.start_pos,
            "target_pos": path_info.target_pos,
            "items": items,
            "obstacles": obstacles
        }