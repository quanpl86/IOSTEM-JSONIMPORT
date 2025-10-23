# src/map_generator/placements/for_loop_placer.py

from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo

class ForLoopPlacer(BasePlacer):
    """
    Đặt các vật phẩm theo một quy luật lặp lại nhất quán.
    
    Placer này được thiết kế để hoạt động với nhiều loại Topology khác nhau
    (StraightLine, Staircase, Square, PlowingField) để tạo ra các thử thách
    về Vòng lặp For. Nó tin tưởng rằng Topology đã cung cấp các tọa độ
    quan trọng trong `path_info.path_coords`.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Nhận một con đường có cấu trúc và đặt một vật phẩm lên mỗi điểm
        quan trọng của con đường đó.

        Args:
            path_info (PathInfo): Thông tin đường đi từ một lớp Topology.
            params (dict): Các tham số bổ sung (không được sử dụng trong placer này).

        Returns:
            dict: Một dictionary chứa layout map hoàn chỉnh.
        """
        print("    LOG: Placing items with 'for_loop' logic...")

        # (CẢI TIẾN) Ưu tiên sử dụng placement_coords nếu có, nếu không thì dùng path_coords
        coords_to_place_on = path_info.placement_coords if path_info.placement_coords else path_info.path_coords

        # Logic cốt lõi: Đặt một vật phẩm ('crystal') tại mỗi tọa độ
        # mà lớp Topology đã xác định là một phần của con đường lặp lại.
        # - Với StraightLine/Staircase, đây là các ô liên tiếp.
        # - Với Square, đây là 4 góc.
        # - Với PlowingField, đây là các ô trên luống cày.
        
        # (SỬA LỖI) Không đặt vật phẩm ở vị trí đích cuối cùng.
        # Điều này áp dụng cho các map như Staircase, PlowingField.
        items = [{"type": "crystal", "pos": pos} for pos in coords_to_place_on if pos != path_info.target_pos]
        
        # Trong các bài toán về vòng lặp for, chúng ta thường không thêm chướng ngại vật
        # để người chơi có thể tập trung hoàn toàn vào việc nhận biết quy luật lặp.
        obstacles = []

        return {
            "start_pos": path_info.start_pos,
            "target_pos": path_info.target_pos,
            "items": items,
            "obstacles": obstacles
        }